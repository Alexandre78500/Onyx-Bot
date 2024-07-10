import discord
from discord.ext import commands
from datetime import datetime, timedelta
import json
import os
import matplotlib.pyplot as plt
import numpy as np

stats_file = "data/message_stats.json"

class Stats2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Charger les données depuis le fichier JSON
        if os.path.exists(stats_file):
            with open(stats_file, 'r') as f:
                self.message_stats = json.load(f)
        else:
            self.message_stats = {}

    def save_stats(self):
        with open(stats_file, 'w') as f:
            json.dump(self.message_stats, f)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        guild_id = str(message.guild.id)
        user_id = str(message.author.id)
        now = datetime.utcnow().isoformat()

        if guild_id not in self.message_stats:
            self.message_stats[guild_id] = {}

        if user_id not in self.message_stats[guild_id]:
            self.message_stats[guild_id][user_id] = []

        self.message_stats[guild_id][user_id].append(now)
        self.save_stats()

    def calculate_stats(self, guild_id, period_hours):
        now = datetime.utcnow()
        cutoff = now - timedelta(hours=period_hours)
        cutoff_iso = cutoff.isoformat()

        stats = {}
        if guild_id in self.message_stats:
            for user_id, timestamps in self.message_stats[guild_id].items():
                count = sum(1 for t in timestamps if t > cutoff_iso)
                if count > 0:
                    stats[user_id] = count

        return stats

    def calculate_growth(self, current, previous):
        growth = {}
        for user_id, current_count in current.items():
            previous_count = previous.get(user_id, 0)
            if previous_count == 0:
                growth[user_id] = float('inf') if current_count > 0 else 0
            else:
                growth[user_id] = ((current_count - previous_count) / previous_count) * 100
        return growth

    @commands.command()
    async def rank2(self, ctx):
        guild_id = str(ctx.guild.id)
        periods = {
            "24h": 24,
            "7d": 24 * 7,
            "30d": 24 * 30,
        }

        current_stats = {period: self.calculate_stats(guild_id, hours) for period, hours in periods.items()}
        previous_stats = {period: self.calculate_stats(guild_id, hours * 2) for period, hours in periods.items()}
        growth = {period: self.calculate_growth(current_stats[period], previous_stats[period]) for period in periods}

        top_users = sorted(current_stats["30d"].items(), key=lambda x: x[1], reverse=True)[:10]

        fig, ax = plt.subplots(figsize=(12, 8))
        ax.axis('off')

        # Couleurs pour le top 3
        colors = ['gold', 'silver', 'peru'] + ['#2f3136'] * (len(top_users) - 3)

        # Créer les données du tableau
        table_data = [["Rank", "User", "Messages (24h)", "Growth (24h)", "Messages (7d)", "Growth (7d)", "Messages (30d)", "Growth (30d)"]]

        for rank, (user_id, count_30d) in enumerate(top_users, start=1):
            user = await self.bot.fetch_user(int(user_id))
            count_24h = current_stats["24h"].get(user_id, 0)
            count_7d = current_stats["7d"].get(user_id, 0)

            growth_24h = self.format_growth(growth["24h"].get(user_id, 0))
            growth_7d = self.format_growth(growth["7d"].get(user_id, 0))
            growth_30d = self.format_growth(growth["30d"].get(user_id, 0))

            table_data.append([rank, user.name, count_24h, growth_24h, count_7d, growth_7d, count_30d, growth_30d])

        # Créer le tableau
        table = ax.table(cellText=table_data, cellLoc='center', loc='center', edges='horizontal')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 1.5)

        # Appliquer les couleurs de fond
        for i, color in enumerate(colors, start=1):
            for j in range(len(table_data[0])):
                table[i, j].set_facecolor(color)

        # Appliquer les styles de texte
        for i, (rank, *row) in enumerate(table_data):
            for j, cell in enumerate(row):
                if i == 0:  # Header row
                    table[i, j].get_text().set_fontweight('bold')  # Set font weight for the header
                    table[i, j].get_text().set_color('white')
                table[i, j].get_text().set_fontsize(12)

        # Définir la couleur de fond pour la figure et l'axe
        fig.patch.set_facecolor('#2f3136')
        ax.patch.set_facecolor('#2f3136')
        table.auto_set_column_width([0, 1, 2, 3, 4, 5, 6, 7])

        plt.tight_layout()
        plt.savefig('rank2.png', bbox_inches='tight', transparent=False)
        plt.close(fig)

        await ctx.send(file=discord.File('rank2.png'))

    def format_growth(self, growth):
        if growth == float('inf'):
            return "∞%"
        color = "green" if growth >= 0 else "red"
        sign = "+" if growth >= 0 else ""
        return f"{sign}{growth:.2f}%"

def setup(bot):
    bot.add_cog(Stats2(bot))
