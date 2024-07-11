import discord
from discord.ext import commands
from datetime import datetime, timedelta, timezone
import json
import os

stats_file = "data/message_stats.json"

class ServerStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Charger les données depuis le fichier JSON pour les messages
        self.message_stats = self.load_stats()

    def load_stats(self):
        if os.path.exists(stats_file):
            try:
                with open(stats_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        else:
            return {}

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
    async def mystats(self, ctx):
        guild_id = str(ctx.guild.id)
        user_id = str(ctx.author.id)

        # Statistiques de messages
        periods = {
            "24h": 24,
            "7d": 24 * 7,
            "30d": 24 * 30,
        }

        current_stats = {period: self.calculate_stats(guild_id, hours) for period, hours in periods.items()}
        previous_stats = {period: self.calculate_stats(guild_id, hours * 2) for period, hours in periods.items()}
        growth = {period: self.calculate_growth(current_stats[period], previous_stats[period]) for period in periods}

        embed = discord.Embed(title=f"Statistiques de {ctx.author.display_name}", color=discord.Color.blue())
        embed.add_field(name="Messages (24h)", value=f"{current_stats['24h'].get(user_id, 0)} {self.format_growth(growth['24h'].get(user_id, 0))}", inline=False)
        embed.add_field(name="Messages (7j)", value=f"{current_stats['7d'].get(user_id, 0)} {self.format_growth(growth['7d'].get(user_id, 0))}", inline=False)
        embed.add_field(name="Messages (30j)", value=f"{current_stats['30d'].get(user_id, 0)} {self.format_growth(growth['30d'].get(user_id, 0))}", inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def rank(self, ctx):
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

        embed = discord.Embed(title="Classement des utilisateurs les plus actifs")

        for rank, (user_id, count_30d) in enumerate(top_users, start=1):
            user = await self.bot.fetch_user(int(user_id))
            count_24h = current_stats["24h"].get(user_id, 0)
            count_7d = current_stats["7d"].get(user_id, 0)

            growth_24h = self.format_growth(growth["24h"].get(user_id, 0))
            growth_7d = self.format_growth(growth["7d"].get(user_id, 0))
            growth_30d = self.format_growth(growth["30d"].get(user_id, 0))

            embed.add_field(
                name=f"{rank}. {user.name}",
                value=(
                    f"**Messages (24h)**: {count_24h} {growth_24h}\n"
                    f"**Messages (7j)**: {count_7d} {growth_7d}\n"
                    f"**Messages (30j)**: {count_30d} {growth_30d}"
                ),
                inline=False
            )
            embed.set_thumbnail(url=user.avatar_url)

        await ctx.send(embed=embed)

    def format_growth(self, growth):
        if growth == float('inf'):
            return "∞%"
        color = "green" if growth >= 0 else "red"
        sign = "+" if growth >= 0 else ""
        return f"```diff\n{sign}{growth:.2f}%```"

def setup(bot):
    bot.add_cog(ServerStats(bot))
