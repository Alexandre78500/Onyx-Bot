import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timezone, timedelta
import random
import json
import os
import matplotlib.pyplot as plt
import calendar
from matplotlib.patches import Rectangle

dreams_file = "data/dreams.json"
CHANNEL_ID = 422870909741957122  # ID du canal channel-des-rl

class DreamJournalReminder(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Charger les données depuis le fichier JSON
        if os.path.exists(dreams_file):
            with open(dreams_file, 'r') as f:
                self.dreams = json.load(f)
        else:
            self.dreams = {}

        # Planifier la notification de rappel chaque matin à 7h UTC+2
        self.scheduler = AsyncIOScheduler()
        self.scheduler.add_job(self.reminder_to_note_dream, 'cron', hour=5, minute=0, timezone='Europe/Paris')
        self.scheduler.start()

    def save_dreams(self):
        with open(dreams_file, 'w') as f:
            json.dump(self.dreams, f)

    async def reminder_to_note_dream(self):
        channel = self.bot.get_channel(CHANNEL_ID)
        if channel:
            await channel.send("Bon matin à tous les rêveurs ! N'oubliez pas de noter vos rêves dans `channel-des-rl`.")

    @commands.command()
    async def dreamcalendar(self, ctx, member: discord.Member = None):
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
    bot.add_cog(DreamJournalReminder(bot))
