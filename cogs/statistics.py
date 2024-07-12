import discord
from discord.ext import commands
from datetime import datetime, timedelta, timezone
import matplotlib.pyplot as plt
import numpy as np
from utils.json_manager import JsonManager

dreams_file = "data/dreams.json"
stats_file = "data/message_stats.json"

class Statistics(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.dreams = JsonManager.load_json(dreams_file, default={})
        self.message_stats = JsonManager.load_json(stats_file, default={})
        self.combo_reset_hour = 3
        self.timezone = timezone(timedelta(hours=2))

    def save_stats(self):
        JsonManager.save_json(stats_file, self.message_stats)

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

    def get_user_dream_stats(self, user_id):
        if user_id not in self.dreams:
            return None, 0, 0
        dreams = self.dreams[user_id]
        total_dreams = len(dreams)
        lucid_dreams = sum(1 for dream in dreams if dream.get("rl", False))
        return dreams, total_dreams, lucid_dreams

    def calculate_combo(self, user_id):
        if user_id not in self.dreams:
            return 0, 0
        dreams = sorted(self.dreams[user_id], key=lambda d: d['date'])
        combo = 0
        max_combo = 0
        last_date = None
        for dream in dreams:
            dream_date = datetime.fromisoformat(dream['date']).astimezone(self.timezone).date()
            if last_date is None:
                combo = 1
            else:
                if (dream_date - last_date).days == 1:
                    combo += 1
                else:
                    combo = 1
            if combo > max_combo:
                max_combo = combo
            last_date = dream_date
        current_date = datetime.now(self.timezone).date()
        if last_date and (current_date - last_date).days > 1:
            combo = 0
        return combo, max_combo

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

    @commands.command(name="dstats")
    async def user_dream_stats(self, ctx, member: discord.Member = None):
        member = member or ctx.author
        user_id = str(member.id)
        dreams, total_dreams, lucid_dreams = self.get_user_dream_stats(user_id)
        combo, max_combo = self.calculate_combo(user_id)

        embed = discord.Embed(title=f"Statistiques de rêve pour {member.display_name}", color=discord.Color.blue())
        embed.add_field(name="Total des rêves", value=total_dreams, inline=True)
        embed.add_field(name="Rêves lucides", value=lucid_dreams, inline=True)
        embed.add_field(name="Combo actuel", value=combo, inline=True)
        embed.add_field(name="Combo maximum", value=max_combo, inline=True)

        await ctx.send(embed=embed)

    @commands.command(name="gstats")
    async def general_dream_stats(self, ctx):
        total_dreams = sum(len(dreams) for dreams in self.dreams.values())
        total_lucid_dreams = sum(sum(1 for dream in dreams if dream.get("rl", False)) for dreams in self.dreams.values())
        total_users = len(self.dreams)

        embed = discord.Embed(title="Statistiques générales des rêves", color=discord.Color.green())
        embed.add_field(name="Total des rêves", value=total_dreams, inline=True)
        embed.add_field(name="Total des rêves lucides", value=total_lucid_dreams, inline=True)
        embed.add_field(name="Nombre d'utilisateurs", value=total_users, inline=True)

        top_dreamers = sorted(self.dreams.items(), key=lambda x: len(x[1]), reverse=True)[:5]
        top_dreamers_text = "\n".join([f"{idx+1}. <@{user_id}>: {len(dreams)} rêves" for idx, (user_id, dreams) in enumerate(top_dreamers)])
        embed.add_field(name="Top 5 des rêveurs", value=top_dreamers_text, inline=False)

        await ctx.send(embed=embed)

    @commands.command(name="mstats")
    async def my_stats(self, ctx):
        guild_id = str(ctx.guild.id)
        user_id = str(ctx.author.id)

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

    @commands.command(name="rank")
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

        await ctx.send(embed=embed)

    @commands.command(name="rankimg")
    async def rank_image(self, ctx):
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

        colors = ['gold', 'silver', 'peru'] + ['#2f3136'] * (len(top_users) - 3)

        table_data = [["Rank", "User", "Messages (24h)", "Growth (24h)", "Messages (7d)", "Growth (7d)", "Messages (30d)", "Growth (30d)"]]

        for rank, (user_id, count_30d) in enumerate(top_users, start=1):
            user = await self.bot.fetch_user(int(user_id))
            count_24h = current_stats["24h"].get(user_id, 0)
            count_7d = current_stats["7d"].get(user_id, 0)

            growth_24h = self.format_growth(growth["24h"].get(user_id, 0))
            growth_7d = self.format_growth(growth["7d"].get(user_id, 0))
            growth_30d = self.format_growth(growth["30d"].get(user_id, 0))

            table_data.append([rank, user.name, count_24h, growth_24h, count_7d, growth_7d, count_30d, growth_30d])

        table = ax.table(cellText=table_data, cellLoc='center', loc='center', edges='horizontal')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 1.5)

        for i, color in enumerate(colors, start=1):
            for j in range(len(table_data[0])):
                table[i, j].set_facecolor(color)

        for i, (rank, *row) in enumerate(table_data):
            for j, cell in enumerate(row):
                if i == 0:  # Header row
                    table[i, j].get_text().set_fontweight('bold')
                    table[i, j].get_text().set_color('white')
                table[i, j].get_text().set_fontsize(12)

        fig.patch.set_facecolor('#2f3136')
        ax.patch.set_facecolor('#2f3136')
        table.auto_set_column_width([0, 1, 2, 3, 4, 5, 6, 7])

        plt.tight_layout()
        plt.savefig('rank.png', bbox_inches='tight', transparent=False)
        plt.close(fig)

        await ctx.send(file=discord.File('rank.png'))

    def format_growth(self, growth):
        if growth == float('inf'):
            return "∞%"
        color = "green" if growth >= 0 else "red"
        sign = "+" if growth >= 0 else ""
        return f"```diff\n{sign}{growth:.2f}%```"

def setup(bot):
    bot.add_cog(Statistics(bot))