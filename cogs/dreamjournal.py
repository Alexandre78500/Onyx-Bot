import discord
from discord.ext import commands
import json
import os
import asyncio
from datetime import datetime, timezone, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import random
import aiofiles
from collections import defaultdict
import math

dreams_file = "data/dreams.json"
CHANNEL_ID = 376777553945296899  # ID du canal général

class DreamJournalInteractive(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Charger les données depuis le fichier JSON
        if os.path.exists(dreams_file):
            with open(dreams_file, 'r') as f:
                self.dreams = json.load(f)
        else:
            self.dreams = {}

        # Stocker l'état de chaque utilisateur
        self.user_states = defaultdict(lambda: {"stage": None, "title": None, "content": []})

        # Planifier la publication d'un rêve aléatoire chaque lundi à 7h UTC+2
        self.scheduler = AsyncIOScheduler()
        self.scheduler.add_job(self.post_random_dream, 'cron', day_of_week='mon', hour=5, minute=0, timezone='Europe/Paris')
        self.scheduler.start()

    async def save_dreams(self):
        async with aiofiles.open(dreams_file, 'w') as f:
            await f.write(json.dumps(self.dreams))

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
    async def interactivedream(self, ctx):
        if ctx.channel.name != "channel-des-rl":
            await ctx.send("Cette commande ne peut être utilisée que dans le canal `channel-des-rl`.")
            return

        embed = discord.Embed(title="Journal des Rêves", description="Choisissez une action :", color=discord.Color.blue())
        embed.add_field(name="1️⃣ Ajouter un rêve", value="Commencez à ajouter un nouveau rêve", inline=False)
        embed.add_field(name="2️⃣ Lister vos rêves", value="Affichez la liste de vos rêves enregistrés", inline=False)
        embed.add_field(name="3️⃣ Supprimer un rêve", value="Supprimez un rêve existant", inline=False)
        embed.add_field(name="4️⃣ Rechercher des rêves", value="Recherchez des rêves par mot-clé", inline=False)
        action_msg = await ctx.send(embed=embed)
        await action_msg.add_reaction('1️⃣')
        await action_msg.add_reaction('2️⃣')
        await action_msg.add_reaction('3️⃣')
        await action_msg.add_reaction('4️⃣')

        def check_reaction(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['1️⃣', '2️⃣', '3️⃣', '4️⃣']

        try:
            reaction, user = await self.bot.wait_for('reaction_add', check=check_reaction, timeout=1800.0)  # 30 minutes
            await action_msg.delete()

            if str(reaction.emoji) == '1️⃣':
                await self.interactive_adddream(ctx)
            elif str(reaction.emoji) == '2️⃣':
                await self.interactive_listdreams(ctx, ctx.author, 1)  # Commencez à la page 1
            elif str(reaction.emoji) == '3️⃣':
                await self.interactive_deletedream(ctx)
            elif str(reaction.emoji) == '4️⃣':
                await self.interactive_searchdreams(ctx)
        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.author.mention}, temps écoulé pour choisir une action. Veuillez recommencer et répondre dans les délais impartis.")
            await action_msg.delete()

    async def interactive_adddream(self, ctx):
        user_id = str(ctx.author.id)
        if self.user_states[user_id]["stage"] is not None:
            await ctx.send(f"{ctx.author.mention}, vous avez déjà une saisie de rêve en cours.")
            return

        self.user_states[user_id]["stage"] = "title"
        embed = discord.Embed(title="Ajouter un rêve", description="Quel est le titre de votre rêve ?", color=discord.Color.blue())
        msg = await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        def check_cancel(reaction, user):
            return user == ctx.author and str(reaction.emoji) == '❌'

        await msg.add_reaction('❌')

        try:
            title_msg = await self.bot.wait_for('message', check=check, timeout=1800.0)  # 30 minutes par message
            title = title_msg.content

            if user_id in self.dreams and any(dream['title'].lower() == title.lower() for dream in self.dreams[user_id]):
                await ctx.send(f"{ctx.author.mention}, vous avez déjà un rêve avec ce titre dans votre journal.")
                self.user_states[user_id]["stage"] = None
                return

            self.user_states[user_id]["title"] = title
            self.user_states[user_id]["stage"] = "content"

            embed = discord.Embed(title="Ajouter un rêve", description="Décrivez votre rêve. Envoyez 'FIN' pour terminer l'ajout.", color=discord.Color.blue())
            await msg.edit(embed=embed)

            content = []
            while True:
                done, pending = await asyncio.wait(
                    [
                        self.bot.wait_for('message', check=check, timeout=1800.0),
                        self.bot.wait_for('reaction_add', check=check_cancel, timeout=1800.0)
                    ],
                    return_when=asyncio.FIRST_COMPLETED
                )
                if done:
                    try:
                        content_msg = done.pop().result()
                        if isinstance(content_msg, discord.Message) and content_msg.content.upper() == 'FIN':
                            break
                        if isinstance(content_msg, discord.Message):
                            content.append(content_msg.content)
                    except asyncio.TimeoutError:
                        break

            content = "\n".join(content)
            date = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=2))).isoformat()

            self.user_states[user_id]["content"] = content

            # Embed de confirmation
            embed = discord.Embed(title="Confirmer le rêve", description=f"**Titre:** {title}\n**Contenu:** {content}\n\nRéagissez avec ✅ pour confirmer, ❌ pour annuler.", color=discord.Color.blue())
            confirmation_msg = await ctx.send(embed=embed)
            await confirmation_msg.add_reaction('✅')
            await confirmation_msg.add_reaction('❌')

            def check_reaction(reaction, user):
                return user == ctx.author and str(reaction.emoji) in ['✅', '❌'] and reaction.message.id == confirmation_msg.id

            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=check_reaction, timeout=1800.0)  # 30 minutes
                if str(reaction.emoji) == '✅':
                    rl = await self.ask_for_rl(ctx)
                    if user_id not in self.dreams:
                        self.dreams[user_id] = []

                    self.dreams[user_id].append({"title": title, "content": content, "date": date, "rl": rl})
                    await self.save_dreams()
                    self.user_states[user_id]["stage"] = None

                    if rl:
                        profile_cog = self.bot.get_cog('Profile')
                        if profile_cog:
                            await profile_cog.add_rl(ctx.author)

                    embed = discord.Embed(title="Rêve ajouté", description=f"Rêve '{title}' ajouté avec succès{' en tant que RL' if rl else ''} !", color=discord.Color.green())
                    await confirmation_msg.edit(embed=embed)
                    await confirmation_msg.clear_reactions()

                    # Supprimer les messages du bot après que le rêve ait été noté
                    await msg.delete()

                else:
                    self.user_states[user_id]["stage"] = None
                    embed = discord.Embed(title="Annulé", description="L'ajout du rêve a été annulé.", color=discord.Color.red())
                    await confirmation_msg.edit(embed=embed)
                    await confirmation_msg.clear_reactions()

                    # Supprimer les messages du bot après que le rêve ait été annulé
                    await msg.delete()
                    await confirmation_msg.delete()

            except asyncio.TimeoutError:
                self.user_states[user_id]["stage"] = None
                await ctx.send(f"{ctx.author.mention}, temps écoulé pour la confirmation. Veuillez recommencer et répondre dans les délais impartis.")
                await msg.delete()
                await confirmation_msg.delete()

        except asyncio.TimeoutError:
            self.user_states[user_id]["stage"] = None
            await ctx.send(f"{ctx.author.mention}, temps écoulé. Veuillez recommencer et répondre dans les délais impartis.")
            await msg.delete()

    async def ask_for_rl(self, ctx):
        embed = discord.Embed(title="Rêve lucide", description="Était-ce un rêve lucide (RL) ? Répondez par oui ou non avec les réactions ci-dessous.", color=discord.Color.blue())
        msg = await ctx.send(embed=embed)
        await msg.add_reaction('✅')
        await msg.add_reaction('❌')

        def check_reaction(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['✅', '❌'] and reaction.message.id == msg.id

        try:
            reaction, user = await self.bot.wait_for('reaction_add', check=check_reaction, timeout=1800.0)  # 30 minutes
            await msg.delete()
            return str(reaction.emoji) == '✅'
        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.author.mention}, temps écoulé pour la réponse. Veuillez recommencer et répondre dans les délais impartis.")
            await msg.delete()
            return False
            
    async def interactive_listdreams(self, ctx, member: discord.Member = None, page: int = 1):
        if ctx.channel.name != "channel-des-rl":
            await ctx.send("Cette commande ne peut être utilisée que dans le canal `channel-des-rl`.")
            return

        if member is None:
            member = ctx.author
        
        user_id = str(member.id)
        if user_id not in self.dreams or not self.dreams[user_id]:
            await ctx.send(f"{member.display_name} n'a pas encore noté de rêves. Utilisez `o!adddream` pour en ajouter.")
            return

        dreams = self.dreams[user_id]
        dreams_per_page = 5
        total_pages = math.ceil(len(dreams) / dreams_per_page)

        if page < 1 or page > total_pages:
            await ctx.send(f"La page {page} n'existe pas. Il y a {total_pages} pages au total.")
            return

        start_index = (page - 1) * dreams_per_page
        end_index = start_index + dreams_per_page
        current_page_dreams = dreams[start_index:end_index]

        embed = discord.Embed(title=f"Rêves notés par {member.display_name} (Page {page}/{total_pages})", color=discord.Color.blue())
        for dream in current_page_dreams:
            title = f"⭐ {dream['title']}" if dream.get("rl", False) else dream["title"]
            date = datetime.fromisoformat(dream["date"]).astimezone(timezone(timedelta(hours=2))).strftime("%Y-%m-%d %H:%M:%S")
            embed.add_field(name=title, value=f"Ajouté le {date}", inline=False)
        
        list_msg = await ctx.send(embed=embed)
        
        # Ajout des réactions pour la navigation
        if total_pages > 1:
            await list_msg.add_reaction('⬅️')  # Flèche gauche pour la page précédente
            await list_msg.add_reaction('➡️')  # Flèche droite pour la page suivante
        await list_msg.add_reaction('🔍')  # Loupe pour visualiser un rêve
        await list_msg.add_reaction('❌')  # Croix pour fermer

        def check_reaction(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['⬅️', '➡️', '🔍', '❌'] and reaction.message.id == list_msg.id

        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=check_reaction, timeout=60.0)
                
                if str(reaction.emoji) == '⬅️' and page > 1:
                    await list_msg.delete()
                    await self.interactive_listdreams(ctx, member, page - 1)
                    return
                elif str(reaction.emoji) == '➡️' and page < total_pages:
                    await list_msg.delete()
                    await self.interactive_listdreams(ctx, member, page + 1)
                    return
                elif str(reaction.emoji) == '🔍':
                    await self.interactive_viewdream(ctx)
                elif str(reaction.emoji) == '❌':
                    await list_msg.delete()
                    return
                
                await list_msg.remove_reaction(reaction, user)
                
            except asyncio.TimeoutError:
                await ctx.send(f"{ctx.author.mention}, temps écoulé pour choisir une action. La liste des rêves sera fermée.")
                await list_msg.delete()
                return

    async def interactive_viewdream(self, ctx):
        user_id = str(ctx.author.id)
        if user_id not in self.dreams:
            await ctx.send("Vous n'avez pas encore noté de rêves.")
            return

        embed = discord.Embed(title="Visualiser un rêve", description="Quel est le titre du rêve que vous souhaitez visualiser ?", color=discord.Color.blue())
        msg = await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            title_msg = await self.bot.wait_for('message', check=check, timeout=1800.0)  # 30 minutes par message
            title = title_msg.content

            for dream in self.dreams[user_id]:
                if dream["title"].lower() == title.lower():
                    embed = discord.Embed(title=dream["title"], description=dream["content"], color=discord.Color.blue())
                    await ctx.send(embed=embed)
                    await msg.delete()
                    await title_msg.delete()
                    return

            await ctx.send(f"Aucun rêve trouvé avec le titre '{title}'.")
            await msg.delete()
            await title_msg.delete()

        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.author.mention}, temps écoulé. Veuillez recommencer et répondre dans les délais impartis.")
            await msg.delete()

    async def interactive_deletedream(self, ctx):
        user_id = str(ctx.author.id)
        if user_id not in self.dreams:
            await ctx.send("Vous n'avez pas encore noté de rêves.")
            return

        embed = discord.Embed(title="Supprimer un rêve", description="Quel est le titre du rêve que vous souhaitez supprimer ?", color=discord.Color.blue())
        msg = await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            title_msg = await self.bot.wait_for('message', check=check, timeout=1800.0)  # 30 minutes par message
            title = title_msg.content

            for dream in self.dreams[user_id]:
                if dream["title"].lower() == title.lower():
                    self.dreams[user_id].remove(dream)
                    await self.save_dreams()
                    await ctx.send(f"Rêve '{title}' supprimé avec succès.")
                    await msg.delete()
                    await title_msg.delete()
                    return

            await ctx.send(f"Aucun rêve trouvé avec le titre '{title}'.")
            await msg.delete()
            await title_msg.delete()

        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.author.mention}, temps écoulé. Veuillez recommencer et répondre dans les délais impartis.")
            await msg.delete()

    async def interactive_searchdreams(self, ctx):
        embed = discord.Embed(title="Rechercher des rêves", description="Entrez un mot-clé pour rechercher dans vos rêves :", color=discord.Color.blue())
        msg = await ctx.send(embed=embed)

        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            query_msg = await self.bot.wait_for('message', check=check, timeout=1800.0)  # 30 minutes par message
            query = query_msg.content.lower()
            results = []

            for user_id, dreams in self.dreams.items():
                for dream in dreams:
                    if query in dream["title"].lower() or query in dream["content"].lower():
                        user = await self.bot.fetch_user(user_id)
                        results.append((user.display_name, dream["title"], dream["date"], dream.get("rl", False)))

            if not results:
                await ctx.send("Aucun rêve trouvé correspondant à votre recherche.")
                await msg.delete()
                await query_msg.delete()
                return

            embed = discord.Embed(title="Résultats de la recherche", color=discord.Color.green())
            for username, title, date, rl in results:
                date = datetime.fromisoformat(date).astimezone(timezone(timedelta(hours=2))).strftime("%Y-%m-%d %H:%M:%S")
                title = f"⭐ {title}" if rl else title
                embed.add_field(name=f"{title} par {username}", value=f"Ajouté le {date}", inline=False)
            
            await ctx.send(embed=embed)
            await msg.delete()
            await query_msg.delete()

        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.author.mention}, temps écoulé pour la recherche. Veuillez recommencer et répondre dans les délais impartis.")
            await msg.delete()
            await query_msg.delete()

def setup(bot):
    bot.add_cog(DreamJournalInteractive(bot))