import discord
from discord.ext import commands
import json
import os
import asyncio
from datetime import datetime, timezone, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import random

dreams_file = "data/dreams.json"
CHANNEL_ID = 376777553945296899  # ID du canal général

class DreamJournal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Charger les données depuis le fichier JSON
        if os.path.exists(dreams_file):
            with open(dreams_file, 'r') as f:
                self.dreams = json.load(f)
        else:
            self.dreams = {}

        # Stocker l'état de chaque utilisateur
        self.user_states = {}

        # Planifier la publication d'un rêve aléatoire chaque lundi à 7h UTC+2
        self.scheduler = AsyncIOScheduler()
        self.scheduler.add_job(self.post_random_dream, 'cron', day_of_week='mon', hour=5, minute=0, timezone='Europe/Paris')
        self.scheduler.start()

    def save_dreams(self):
        with open(dreams_file, 'w') as f:
            json.dump(self.dreams, f)

    async def post_random_dream(self):
        channel = self.bot.get_channel(CHANNEL_ID)
        if not channel:
            print("Channel not found")
            return

        one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        dreams_from_last_week = [dream for dreams in self.dreams.values() for dream in dreams if datetime.fromisoformat(dream['date']) > one_week_ago]

        if not dreams_from_last_week:
            await channel.send("Pas de rêves la semaine dernière. Faites un effort, les rêveurs !")
            return

        selected_dream = random.choice(dreams_from_last_week)
        user = self.bot.get_user(int(selected_dream['user_id']))
        if not user:
            print("User not found")
            return

        embed = discord.Embed(title=selected_dream['title'], description=selected_dream['content'], color=discord.Color.blue(), timestamp=datetime.fromisoformat(selected_dream['date']))
        embed.set_author(name=user.name, icon_url=user.avatar_url)
        await channel.send(embed=embed)

    @commands.command()
    async def adddream(self, ctx):
        if ctx.channel.name != "channel-des-rl":
            await ctx.send("Cette commande ne peut être utilisée que dans le canal `channel-des-rl`.")
            return

        user_id = str(ctx.author.id)
        if user_id in self.user_states:
            await ctx.send(f"{ctx.author.mention}, vous avez déjà une saisie de rêve en cours.")
            return

        self.user_states[user_id] = {'stage': 'title'}

        prompt_msg1 = await ctx.send(f"{ctx.author.mention}, quel est le titre de votre rêve ?")

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            title_msg = await self.bot.wait_for('message', check=check, timeout=60.0)
            title = title_msg.content

            # Vérifier les doublons de titres dans le journal de l'utilisateur
            if user_id in self.dreams and any(dream['title'].lower() == title.lower() for dream in self.dreams[user_id]):
                await ctx.send(f"{ctx.author.mention}, vous avez déjà un rêve avec ce titre dans votre journal.")
                del self.user_states[user_id]
                return

            self.user_states[user_id]['title'] = title
            self.user_states[user_id]['stage'] = 'content'

            prompt_msg2 = await ctx.send(f"{ctx.author.mention}, merci ! Maintenant, décrivez votre rêve. Envoyez 'FIN' pour terminer l'ajout.")

            content = []
            while True:
                content_msg = await self.bot.wait_for('message', check=check, timeout=1800.0)  # 30 minutes
                if content_msg.content.upper() == 'FIN':
                    break
                content.append(content_msg.content)

            content = "\n".join(content)

            # Convertir l'heure UTC en heure française (UTC+2)
            date = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=2))).isoformat()

            await ctx.send(f"{ctx.author.mention}, était-ce un rêve lucide (RL) ? Répondez par oui ou non.")

            try:
                rl_msg = await self.bot.wait_for('message', check=check, timeout=60.0)
                rl = rl_msg.content.lower() in ["oui", "yes", "y"]

                if user_id not in self.dreams:
                    self.dreams[user_id] = []

                self.dreams[user_id].append({"title": title, "content": content, "date": date, "rl": rl})
                self.save_dreams()
                del self.user_states[user_id]

                if rl:
                    # Ajouter un RL au profil de l'utilisateur
                    profile_cog = self.bot.get_cog('Profile')
                    if profile_cog:
                        await profile_cog.add_rl(ctx.author)

                await ctx.send(f"{ctx.author.mention}, rêve '{title}' ajouté avec succès{' en tant que RL' if rl else ''} ! Continuez à noter vos rêves pour progresser !")

                # Supprimer les messages du bot après que le rêve ait été noté
                await prompt_msg1.delete()
                await prompt_msg2.delete()

            except asyncio.TimeoutError:
                await ctx.send(f"{ctx.author.mention}, temps écoulé pour la réponse. Veuillez recommencer et répondre dans les délais impartis.")

        except asyncio.TimeoutError:
            del self.user_states[user_id]
            await ctx.send(f"{ctx.author.mention}, temps écoulé. Veuillez recommencer et répondre dans les délais impartis.")

    @commands.command()
    async def listdreams(self, ctx, member: discord.Member = None):
        if ctx.channel.name != "channel-des-rl":
            await ctx.send("Cette commande ne peut être utilisée que dans le canal `channel-des-rl`.")
            return

        if member is None:
            member = ctx.author
        
        user_id = str(member.id)
        if user_id not in self.dreams or not self.dreams[user_id]:
            await ctx.send(f"{member.display_name} n'a pas encore noté de rêves. Utilisez `o!adddream` pour en ajouter.")
            return

        embed = discord.Embed(title=f"Rêves notés par {member.display_name}", color=discord.Color.blue())
        for dream in self.dreams[user_id]:
            title = f"⭐ {dream['title']}" if dream.get("rl", False) else dream["title"]
            # Convertir l'heure UTC en heure française (UTC+2) pour l'affichage
            date = datetime.fromisoformat(dream["date"]).astimezone(timezone(timedelta(hours=2))).strftime("%Y-%m-%d %H:%M:%S")
            embed.add_field(name=title, value=f"Ajouté le {date}", inline=False)
        
        await ctx.send(embed=embed)

    @commands.command()
    async def viewdream(self, ctx, *, title: str):
        if ctx.channel.name != "channel-des-rl":
            await ctx.send("Cette commande ne peut être utilisée que dans le canal `channel-des-rl`.")
            return

        user_id = str(ctx.author.id)
        if user_id not in self.dreams:
            await ctx.send("Vous n'avez pas encore noté de rêves.")
            return

        for dream in self.dreams[user_id]:
            if dream["title"].lower() == title.lower():
                embed = discord.Embed(title=dream["title"], description=dream["content"], color=discord.Color.blue())
                await ctx.send(embed=embed)
                return

        await ctx.send(f"Aucun rêve trouvé avec le titre '{title}'.")

    @commands.command()
    async def deletedream(self, ctx, *, title: str):
        if ctx.channel.name != "channel-des-rl":
            await ctx.send("Cette commande ne peut être utilisée que dans le canal `channel-des-rl`.")
            return

        user_id = str(ctx.author.id)
        if user_id not in self.dreams:
            await ctx.send("Vous n'avez pas encore noté de rêves.")
            return

        for dream in self.dreams[user_id]:
            if dream["title"].lower() == title.lower():
                self.dreams[user_id].remove(dream)
                self.save_dreams()
                await ctx.send(f"Rêve '{title}' supprimé avec succès.")
                return

        await ctx.send(f"Aucun rêve trouvé avec le titre '{title}'.")

    @commands.command()
    async def searchdreams(self, ctx, *, query: str):
        if ctx.channel.name != "channel-des-rl":
            await ctx.send("Cette commande ne peut être utilisée que dans le canal `channel-des-rl`.")
            return

        results = []
        query = query.lower()
        for user_id, dreams in self.dreams.items():
            for dream in dreams:
                if query in dream["title"].lower() or query in dream["content"].lower():
                    user = await self.bot.fetch_user(user_id)
                    results.append((user.display_name, dream["title"], dream["date"], dream.get("rl", False)))

        if not results:
            await ctx.send("Aucun rêve trouvé correspondant à votre recherche.")
            return

        embed = discord.Embed(title="Résultats de la recherche", color=discord.Color.green())
        for username, title, date, rl in results:
            date = datetime.fromisoformat(date).astimezone(timezone(timedelta(hours=2))).strftime("%Y-%m-%d %H:%M:%S")
            title = f"⭐ {title}" if rl else title
            embed.add_field(name=f"{title} par {username}", value=f"Ajouté le {date}", inline=False)
        
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(DreamJournal(bot))
