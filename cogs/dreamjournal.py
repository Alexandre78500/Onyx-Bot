import discord
from discord.ext import commands
import asyncio
from datetime import datetime, timezone, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import random
from collections import defaultdict
import math
import matplotlib.pyplot as plt
import calendar
from matplotlib.patches import Rectangle
from utils.json_manager import JsonManager
import logging

dreams_file = "data/dreams.json"
CHANNEL_ID_GENERAL = 376777553945296899  # ID du canal général
CHANNEL_ID_RL = 422870909741957122  # ID du canal channel-des-rl

logger = logging.getLogger('bot.dreamjournal')

class DreamJournal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dreams = JsonManager.load_json(dreams_file, default={})
        self.user_states = defaultdict(lambda: {"stage": None, "title": None, "content": []})
        self.timezone = timezone(timedelta(hours=2))

        # Planifier les tâches
        self.scheduler = AsyncIOScheduler()
        self.scheduler.add_job(self.post_random_dream, 'cron', day_of_week='mon', hour=5, minute=0, timezone='Europe/Paris')
        self.scheduler.add_job(self.reminder_to_note_dream, 'cron', hour=5, minute=0, timezone='Europe/Paris')
        self.scheduler.start()

    async def save_dreams(self):
        JsonManager.save_json(dreams_file, self.dreams)

    async def post_random_dream(self):
        channel = self.bot.get_channel(CHANNEL_ID_GENERAL)
        if not channel:
            logger.error("Channel not found for posting random dream")
            return

        one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        dreams_from_last_week = [
            dream for dreams in self.dreams.values() 
            for dream in dreams 
            if datetime.fromisoformat(dream['date']) > one_week_ago
        ]

        if not dreams_from_last_week:
            await channel.send("Pas de rêves la semaine dernière. Faites un effort, les rêveurs !")
            return

        selected_dream = random.choice(dreams_from_last_week)
        user = self.bot.get_user(int(selected_dream['user_id']))
        if not user:
            logger.error(f"User not found for dream: {selected_dream['user_id']}")
            return

        embed = discord.Embed(
            title=selected_dream['title'],
            description=selected_dream['content'],
            color=discord.Color.blue(),
            timestamp=datetime.fromisoformat(selected_dream['date'])
        )
        embed.set_author(name=user.name, icon_url=user.avatar_url)
        await channel.send(embed=embed)

    async def reminder_to_note_dream(self):
        channel = self.bot.get_channel(CHANNEL_ID_RL)
        if channel:
            await channel.send("Bon matin à tous les rêveurs ! N'oubliez pas de noter vos rêves dans `channel-des-rl`.")
        else:
            logger.error("Channel not found for dream reminder")

    @commands.command()
    async def interactivedream(self, ctx):
        logger.info(f"Interactivedream command invoked by {ctx.author}")
        if ctx.channel.name != "channel-des-rl":
            await ctx.send("Cette commande ne peut être utilisée que dans le canal `channel-des-rl`.")
            return

        embed = discord.Embed(title="Journal des Rêves", description="Choisissez une action :", color=discord.Color.blue())
        actions = [
            ("1️⃣", "Ajouter un rêve", "Commencez à ajouter un nouveau rêve"),
            ("2️⃣", "Lister vos rêves", "Affichez la liste de vos rêves enregistrés"),
            ("3️⃣", "Supprimer un rêve", "Supprimez un rêve existant"),
            ("4️⃣", "Rechercher des rêves", "Recherchez des rêves par mot-clé")
        ]

        for emoji, name, description in actions:
            embed.add_field(name=f"{emoji} {name}", value=description, inline=False)

        action_msg = await ctx.send(embed=embed)
        for emoji, _, _ in actions:
            await action_msg.add_reaction(emoji)

        def check_reaction(reaction, user):
            return user == ctx.author and str(reaction.emoji) in [emoji for emoji, _, _ in actions]

        try:
            reaction, user = await self.bot.wait_for('reaction_add', check=check_reaction, timeout=1800.0)
            await action_msg.delete()

            if str(reaction.emoji) == '1️⃣':
                await self.interactive_adddream(ctx)
            elif str(reaction.emoji) == '2️⃣':
                await self.interactive_listdreams(ctx, ctx.author, 1)
            elif str(reaction.emoji) == '3️⃣':
                await self.interactive_deletedream(ctx)
            elif str(reaction.emoji) == '4️⃣':
                await self.interactive_searchdreams(ctx)

        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.author.mention}, temps écoulé pour choisir une action. Veuillez recommencer.")

    async def interactive_adddream(self, ctx):
        user_id = str(ctx.author.id)
        if self.user_states[user_id]["stage"] is not None:
            await ctx.send(f"{ctx.author.mention}, vous avez déjà une saisie de rêve en cours.")
            return

        self.user_states[user_id]["stage"] = "title"
        embed = discord.Embed(title="Ajouter un rêve", description="Quel est le titre de votre rêve ?", color=discord.Color.blue())
        msg = await ctx.send(embed=embed)
        await msg.add_reaction('❌')

        def check_message(m):
            return m.author == ctx.author and m.channel == ctx.channel

        def check_reaction(reaction, user):
            return user == ctx.author and str(reaction.emoji) == '❌' and reaction.message.id == msg.id

        try:
            done, pending = await asyncio.wait([
                self.bot.wait_for('message', check=check_message, timeout=1800.0),
                self.bot.wait_for('reaction_add', check=check_reaction, timeout=1800.0)
            ], return_when=asyncio.FIRST_COMPLETED)

            try:
                stuff = done.pop().result()
            except asyncio.TimeoutError:
                await ctx.send(f"{ctx.author.mention}, temps écoulé. Veuillez recommencer.")
                self.user_states[user_id]["stage"] = None
                for future in done:
                    future.exception()
                for future in pending:
                    future.cancel()
                await msg.delete()
                return

            for future in pending:
                future.cancel()

            if isinstance(stuff, discord.Message):
                title = stuff.content
            else:
                await ctx.send(f"{ctx.author.mention}, ajout du rêve annulé.")
                self.user_states[user_id]["stage"] = None
                await msg.delete()
                return

            if user_id in self.dreams and any(dream['title'].lower() == title.lower() for dream in self.dreams[user_id]):
                await ctx.send(f"{ctx.author.mention}, vous avez déjà un rêve avec ce titre dans votre journal.")
                self.user_states[user_id]["stage"] = None
                await msg.delete()
                return

            self.user_states[user_id]["title"] = title
            self.user_states[user_id]["stage"] = "content"

            embed = discord.Embed(title="Ajouter un rêve", description="Décrivez votre rêve. Envoyez 'FIN' pour terminer l'ajout.", color=discord.Color.blue())
            await msg.edit(embed=embed)

            content = await self.wait_for_dream_content(ctx, 1800.0)
            if content is None:
                self.user_states[user_id]["stage"] = None
                await msg.delete()
                return

            date = datetime.now(timezone.utc).astimezone(timezone(timedelta(hours=2))).isoformat()

            if await self.confirm_dream(ctx, title, content):
                rl = await self.ask_for_rl(ctx)
                if user_id not in self.dreams:
                    self.dreams[user_id] = []

                self.dreams[user_id].append({"title": title, "content": content, "date": date, "rl": rl})
                await self.save_dreams()

                if rl:
                    profile_cog = self.bot.get_cog('Profile')
                    if profile_cog:
                        await profile_cog.add_rl(ctx.author)

                embed = discord.Embed(title="Rêve ajouté", description=f"Rêve '{title}' ajouté avec succès{' en tant que RL' if rl else ''} !", color=discord.Color.green())
                await ctx.send(embed=embed)

            self.user_states[user_id]["stage"] = None
            await msg.delete()

        except asyncio.TimeoutError:
            self.user_states[user_id]["stage"] = None
            await ctx.send(f"{ctx.author.mention}, temps écoulé. Veuillez recommencer.")
            await msg.delete()

    async def wait_for_text_input(self, ctx, timeout):
        def check(m):
            return m.author == ctx.author and m.channel == ctx.channel

        try:
            message = await self.bot.wait_for('message', check=check, timeout=timeout)
            return message.content
        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.author.mention}, temps écoulé. Veuillez recommencer.")
            return None

    async def wait_for_dream_content(self, ctx, timeout):
        content = []
        while True:
            input_text = await self.wait_for_text_input(ctx, timeout)
            if input_text is None:
                return None
            if input_text.upper() == 'FIN':
                break
            content.append(input_text)
        return "\n".join(content)

    async def confirm_dream(self, ctx, title, content):
        embed = discord.Embed(title="Confirmer le rêve", description=f"**Titre:** {title}\n**Contenu:** {content}\n\nRéagissez avec ✅ pour confirmer, ❌ pour annuler.", color=discord.Color.blue())
        confirmation_msg = await ctx.send(embed=embed)
        await confirmation_msg.add_reaction('✅')
        await confirmation_msg.add_reaction('❌')

        def check_reaction(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['✅', '❌'] and reaction.message.id == confirmation_msg.id

        try:
            reaction, user = await self.bot.wait_for('reaction_add', check=check_reaction, timeout=1800.0)
            await confirmation_msg.delete()
            return str(reaction.emoji) == '✅'
        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.author.mention}, temps écoulé pour la confirmation. Veuillez recommencer.")
            await confirmation_msg.delete()
            return False

    async def ask_for_rl(self, ctx):
        embed = discord.Embed(title="Rêve lucide", description="Était-ce un rêve lucide (RL) ? Répondez par oui ou non avec les réactions ci-dessous.", color=discord.Color.blue())
        msg = await ctx.send(embed=embed)
        await msg.add_reaction('✅')
        await msg.add_reaction('❌')

        def check_reaction(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['✅', '❌'] and reaction.message.id == msg.id

        try:
            reaction, user = await self.bot.wait_for('reaction_add', check=check_reaction, timeout=1800.0)
            await msg.delete()
            return str(reaction.emoji) == '✅'
        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.author.mention}, temps écoulé pour la réponse. Veuillez recommencer.")
            await msg.delete()
            return False

    async def interactive_listdreams(self, ctx, member: discord.Member = None, page: int = 1):
        if ctx.channel.name != "channel-des-rl":
            await ctx.send("Cette commande ne peut être utilisée que dans le canal `channel-des-rl`.")
            return

        member = member or ctx.author
        user_id = str(member.id)
        
        if user_id not in self.dreams or not self.dreams[user_id]:
            await ctx.send(f"{member.display_name} n'a pas encore noté de rêves.")
            return

        dreams = self.dreams[user_id]
        dreams_per_page = 5
        total_pages = math.ceil(len(dreams) / dreams_per_page)

        if page < 1 or page > total_pages:
            await ctx.send(f"La page {page} n'existe pas. Il y a {total_pages} pages au total.")
            return

        embed = self.create_dreams_list_embed(member, dreams, page, total_pages, dreams_per_page)
        list_msg = await ctx.send(embed=embed)
        
        await self.add_navigation_reactions(list_msg, total_pages)

        while True:
            try:
                reaction, user = await self.wait_for_dream_list_reaction(ctx, list_msg)
                
                if str(reaction.emoji) == '⬅️' and page > 1:
                    page -= 1
                elif str(reaction.emoji) == '➡️' and page < total_pages:
                    page += 1
                elif str(reaction.emoji) == '🔍':
                    await self.interactive_viewdream(ctx)
                    return
                elif str(reaction.emoji) == '❌':
                    await list_msg.delete()
                    return
                
                embed = self.create_dreams_list_embed(member, dreams, page, total_pages, dreams_per_page)
                await list_msg.edit(embed=embed)
                await list_msg.remove_reaction(reaction, user)
                
            except asyncio.TimeoutError:
                await ctx.send(f"{ctx.author.mention}, temps écoulé. La liste des rêves sera fermée.")
                await list_msg.delete()
                return

    def create_dreams_list_embed(self, member, dreams, page, total_pages, dreams_per_page):
        start_index = (page - 1) * dreams_per_page
        end_index = start_index + dreams_per_page
        current_page_dreams = dreams[start_index:end_index]

        embed = discord.Embed(title=f"Rêves notés par {member.display_name} (Page {page}/{total_pages})", color=discord.Color.blue())
        for dream in current_page_dreams:
            title = f"⭐ {dream['title']}" if dream.get("rl", False) else dream["title"]
            date = datetime.fromisoformat(dream["date"]).astimezone(timezone(timedelta(hours=2))).strftime("%Y-%m-%d %H:%M:%S")
            embed.add_field(name=title, value=f"Ajouté le {date}", inline=False)
        
        return embed

    async def add_navigation_reactions(self, message, total_pages):
        if total_pages > 1:
            await message.add_reaction('⬅️')
            await message.add_reaction('➡️')
        await message.add_reaction('🔍')
        await message.add_reaction('❌')

    async def wait_for_dream_list_reaction(self, ctx, message):
        def check_reaction(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['⬅️', '➡️', '🔍', '❌'] and reaction.message.id == message.id

        return await self.bot.wait_for('reaction_add', check=check_reaction, timeout=60.0)

    async def interactive_viewdream(self, ctx):
        user_id = str(ctx.author.id)
        if user_id not in self.dreams:
            await ctx.send("Vous n'avez pas encore noté de rêves.")
            return

        embed = discord.Embed(title="Visualiser un rêve", description="Quel est le titre du rêve que vous souhaitez visualiser ?", color=discord.Color.blue())
        msg = await ctx.send(embed=embed)

        try:
            title = await self.wait_for_text_input(ctx, 1800.0)
            if title is None:
                return

            dream = next((dream for dream in self.dreams[user_id] if dream["title"].lower() == title.lower()), None)
            if dream:
                embed = discord.Embed(title=dream["title"], description=dream["content"], color=discord.Color.blue())
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"Aucun rêve trouvé avec le titre '{title}'.")

        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.author.mention}, temps écoulé. Veuillez recommencer.")
        
        finally:
            await msg.delete()

    async def interactive_deletedream(self, ctx):
        user_id = str(ctx.author.id)
        if user_id not in self.dreams:
            await ctx.send("Vous n'avez pas encore noté de rêves.")
            return

        embed = discord.Embed(title="Supprimer un rêve", description="Quel est le titre du rêve que vous souhaitez supprimer ?", color=discord.Color.blue())
        msg = await ctx.send(embed=embed)

        try:
            title = await self.wait_for_text_input(ctx, 1800.0)
            if title is None:
                return

            dream = next((dream for dream in self.dreams[user_id] if dream["title"].lower() == title.lower()), None)
            if dream:
                self.dreams[user_id].remove(dream)
                await self.save_dreams()
                await ctx.send(f"Rêve '{title}' supprimé avec succès.")
            else:
                await ctx.send(f"Aucun rêve trouvé avec le titre '{title}'.")

        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.author.mention}, temps écoulé. Veuillez recommencer.")
        
        finally:
            await msg.delete()

    async def interactive_searchdreams(self, ctx):
        embed = discord.Embed(title="Rechercher des rêves", description="Entrez un mot-clé pour rechercher dans vos rêves :", color=discord.Color.blue())
        msg = await ctx.send(embed=embed)

        try:
            query = await self.wait_for_text_input(ctx, 1800.0)
            if query is None:
                return

            results = self.search_dreams(query.lower())

            if not results:
                await ctx.send("Aucun rêve trouvé correspondant à votre recherche.")
                return

            await self.display_search_results(ctx, results)

        except asyncio.TimeoutError:
            await ctx.send(f"{ctx.author.mention}, temps écoulé pour la recherche. Veuillez recommencer.")
        
        finally:
            await msg.delete()

    def search_dreams(self, query):
        results = []
        for user_id, dreams in self.dreams.items():
            for dream in dreams:
                if query in dream["title"].lower() or query in dream["content"].lower():
                    results.append((user_id, dream))
        return results

    async def display_search_results(self, ctx, results):
        embed = discord.Embed(title="Résultats de la recherche", color=discord.Color.green())
        for user_id, dream in results:
            user = await self.bot.fetch_user(user_id)
            title = f"⭐ {dream['title']}" if dream.get("rl", False) else dream["title"]
            date = datetime.fromisoformat(dream["date"]).astimezone(timezone(timedelta(hours=2))).strftime("%Y-%m-%d %H:%M:%S")
            embed.add_field(name=f"{title} par {user.display_name}", value=f"Ajouté le {date}", inline=False)
        
        await ctx.send(embed=embed)

    @commands.command()
    async def dreamcalendar(self, ctx, member: discord.Member = None):
        logger.info(f"Dreamcalendar command invoked by {ctx.author}")
        if member is None:
            member = ctx.author

        user_id = str(member.id)
        if user_id not in self.dreams or not self.dreams[user_id]:
            await ctx.send(f"{member.display_name} n'a pas encore noté de rêves.")
            return

        dreams_dates = [datetime.fromisoformat(dream['date']).date() for dream in self.dreams[user_id]]
        lucid_dreams_dates = [datetime.fromisoformat(dream['date']).date() for dream in self.dreams[user_id] if dream.get('rl', False)]

        # Configuration du calendrier
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.set_facecolor('#2f3136')  # Fond gris foncé comme Discord

        cal = calendar.Calendar()
        year, month = datetime.now().year, datetime.now().month
        month_days = cal.monthdayscalendar(year, month)

        # Définir les jours de la semaine
        days_of_week = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']
        for i, day in enumerate(days_of_week):
            ax.text(i + 0.5, len(month_days) + 0.5, day, ha='center', va='center', color='white', weight='bold', fontsize=12)

        # Couleurs et formes pour les jours avec des rêves
        for week_num, week in enumerate(month_days):
            for day_num, day in enumerate(week):
                if day == 0:
                    continue
                date = datetime(year, month, day).date()
                if date in lucid_dreams_dates:
                    ax.add_patch(Rectangle((day_num, len(month_days) - week_num - 1), 1, 1, edgecolor='gold', facecolor='gold', alpha=0.5))
                    ax.text(day_num + 0.5, len(month_days) - week_num - 0.5, str(day), ha='center', va='center', color='black', weight='bold', fontsize=10)
                elif date in dreams_dates:
                    ax.add_patch(Rectangle((day_num, len(month_days) - week_num - 1), 1, 1, edgecolor='deepskyblue', facecolor='deepskyblue', alpha=0.5))
                    ax.text(day_num + 0.5, len(month_days) - week_num - 0.5, str(day), ha='center', va='center', color='black', fontsize=10)
                else:
                    ax.text(day_num + 0.5, len(month_days) - week_num - 0.5, str(day), ha='center', va='center', color='grey', fontsize=10)

        # Légende
        legend_elements = [
            Rectangle((0, 0), 1, 1, edgecolor='deepskyblue', facecolor='deepskyblue', alpha=0.5, label='Rêve noté'),
            Rectangle((0, 0), 1, 1, edgecolor='gold', facecolor='gold', alpha=0.5, label='Rêve lucide')
        ]
        ax.legend(handles=legend_elements, loc='lower right', fontsize=10, facecolor='#2f3136', edgecolor='white')

        ax.set_xlim(0, 7)
        ax.set_ylim(0, len(month_days))
        ax.axis('off')
        ax.set_title(f"Calendrier des rêves de {member.display_name} - {calendar.month_name[month]} {year}", color='white', fontsize=14)

        file_path = f"data/{user_id}_calendar.png"
        plt.savefig(file_path, bbox_inches='tight', dpi=100, facecolor='#2f3136')
        plt.close(fig)

        await ctx.send(file=discord.File(file_path))

def setup(bot):
    bot.add_cog(DreamJournal(bot))