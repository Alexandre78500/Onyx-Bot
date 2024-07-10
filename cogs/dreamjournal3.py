import discord
from discord.ext import commands
import json
import os
from datetime import datetime, timezone, timedelta

dreams_file = "data/dreams.json"

class DreamJournalStats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Charger les données depuis le fichier JSON
        if os.path.exists(dreams_file):
            with open(dreams_file, 'r') as f:
                self.dreams = json.load(f)
        else:
            self.dreams = {}

        self.timezone = timezone(timedelta(hours=2))  # Heure de Paris

    def save_dreams(self):
        with open(dreams_file, 'w') as f:
            json.dump(self.dreams, f)

    def calculate_user_stats(self, user_id):
        dreams = self.dreams.get(user_id, [])
        total_dreams = len(dreams)
        lucid_dreams = sum(1 for dream in dreams if dream.get("rl", False))
        first_dream_date = min(dreams, key=lambda d: d['date'])['date'] if dreams else None
        last_dream_date = max(dreams, key=lambda d: d['date'])['date'] if dreams else None
        average_dream_length = sum(len(dream['content'].split()) for dream in dreams) / total_dreams if total_dreams > 0 else 0
        total_words = sum(len(dream['content'].split()) for dream in dreams)

        # Calcul du combo le plus long
        sorted_dreams = sorted(dreams, key=lambda d: d['date'])
        max_combo = 0
        current_combo = 0
        last_date = None

        for dream in sorted_dreams:
            dream_date = datetime.fromisoformat(dream['date']).date()
            if last_date is None:
                current_combo = 1
            elif (dream_date - last_date).days == 1:
                current_combo += 1
            else:
                current_combo = 1
            max_combo = max(max_combo, current_combo)
            last_date = dream_date

        # Répartition des rêves par jour de la semaine
        dreams_per_day_of_week = [0] * 7
        for dream in dreams:
            dream_date = datetime.fromisoformat(dream['date']).astimezone(self.timezone).date()
            dreams_per_day_of_week[dream_date.weekday()] += 1

        # Répartition des rêves par heure
        dreams_per_hour = [0] * 24
        for dream in dreams:
            dream_time = datetime.fromisoformat(dream['date']).astimezone(self.timezone).time()
            dreams_per_hour[dream_time.hour] += 1

        # Moyennes de rêves par jour, semaine, mois
        total_days = (datetime.now(self.timezone).date() - datetime.fromisoformat(first_dream_date).astimezone(self.timezone).date()).days + 1 if first_dream_date else 0
        if total_days >= 7:
            dreams_per_day = total_dreams / total_days
            dreams_per_week = dreams_per_day * 7
            dreams_per_month = dreams_per_day * 30
        else:
            dreams_per_day = "N/A"
            dreams_per_week = "N/A"
            dreams_per_month = "N/A"

        return {
            "total_dreams": total_dreams,
            "lucid_dreams": lucid_dreams,
            "first_dream_date": first_dream_date,
            "last_dream_date": last_dream_date,
            "max_combo": max_combo,
            "average_dream_length": average_dream_length,
            "total_words": total_words,
            "dreams_per_day_of_week": dreams_per_day_of_week,
            "dreams_per_hour": dreams_per_hour,
            "dreams_per_day": dreams_per_day,
            "dreams_per_week": dreams_per_week,
            "dreams_per_month": dreams_per_month
        }

    def calculate_general_stats(self):
        total_dreams = sum(len(dreams) for dreams in self.dreams.values())
        lucid_dreams = sum(dream.get("rl", False) for dreams in self.dreams.values() for dream in dreams)
        longest_dream = max((dream for dreams in self.dreams.values() for dream in dreams), key=lambda d: len(d['content'].split()), default=None)
        shortest_dream = min((dream for dreams in self.dreams.values() for dream in dreams), key=lambda d: len(d['content'].split()), default=None)
        total_words = sum(len(dream['content'].split()) for dreams in self.dreams.values() for dream in dreams)

        top_users = sorted(self.dreams.items(), key=lambda item: len(item[1]), reverse=True)[:10]

        # Répartition des rêves par jour de la semaine
        dreams_per_day_of_week = [0] * 7
        for dreams in self.dreams.values():
            for dream in dreams:
                dream_date = datetime.fromisoformat(dream['date']).astimezone(self.timezone).date()
                dreams_per_day_of_week[dream_date.weekday()] += 1

        # Répartition des rêves par mois
        dreams_per_month = [0] * 12
        for dreams in self.dreams.values():
            for dream in dreams:
                dream_date = datetime.fromisoformat(dream['date']).astimezone(self.timezone).date()
                dreams_per_month[dream_date.month - 1] += 1

        return {
            "total_dreams": total_dreams,
            "lucid_dreams": lucid_dreams,
            "longest_dream": longest_dream,
            "shortest_dream": shortest_dream,
            "total_words": total_words,
            "top_users": top_users,
            "dreams_per_day_of_week": dreams_per_day_of_week,
            "dreams_per_month": dreams_per_month
        }

    @commands.command()
    async def userdreamstats(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        user_id = str(member.id)
        stats = self.calculate_user_stats(user_id)

        embed = discord.Embed(title=f"Statistiques des rêves de {member.display_name}", color=discord.Color.blue())
        embed.add_field(name="Nombre total de rêves", value=stats["total_dreams"], inline=False)
        embed.add_field(name="Nombre de rêves lucides", value=stats["lucid_dreams"], inline=False)
        embed.add_field(name="Pourcentage de rêves lucides", value=f"{(stats['lucid_dreams'] / stats['total_dreams']) * 100:.2f}%" if stats["total_dreams"] > 0 else "N/A", inline=False)
        embed.add_field(name="Date du premier rêve", value=datetime.fromisoformat(stats["first_dream_date"]).strftime('%d %B %Y') if stats["first_dream_date"] else "N/A", inline=False)
        embed.add_field(name="Date du dernier rêve", value=datetime.fromisoformat(stats["last_dream_date"]).strftime('%d %B %Y') if stats["last_dream_date"] else "N/A", inline=False)
        embed.add_field(name="Combo de rêve le plus long", value=stats["max_combo"], inline=False)
        embed.add_field(name="Longueur moyenne des rêves", value=f"{stats['average_dream_length']:.2f} mots", inline=False)
        embed.add_field(name="Nombre de mots total noté", value=stats["total_words"], inline=False)
        embed.add_field(name="Nombre de rêves par jour", value=f"{stats['dreams_per_day']:.2f}" if stats["dreams_per_day"] != "N/A" else "N/A", inline=False)
        embed.add_field(name="Nombre de rêves par semaine", value=f"{stats['dreams_per_week']:.2f}" if stats["dreams_per_week"] != "N/A" else "N/A", inline=False)
        embed.add_field(name="Nombre de rêves par mois", value=f"{stats['dreams_per_month']:.2f}" if stats["dreams_per_month"] != "N/A" else "N/A", inline=False)
        embed.add_field(name="Répartition des rêves par jour de la semaine", value=", ".join([f"{day}: {count}" for day, count in zip(['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'], stats["dreams_per_day_of_week"])]), inline=False)
        embed.add_field(name="Répartition des rêves par heure", value=", ".join([f"{hour}h: {count}" for hour, count in enumerate(stats["dreams_per_hour"])]), inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def generaldreamstats(self, ctx):
        stats = self.calculate_general_stats()

        embed = discord.Embed(title="Statistiques générales des rêves", color=discord.Color.green())
        embed.add_field(name="Nombre total de rêves", value=stats["total_dreams"], inline=False)
        embed.add_field(name="Nombre total de rêves lucides", value=stats["lucid_dreams"], inline=False)
        embed.add_field(name="Pourcentage de rêves lucides", value=f"{(stats['lucid_dreams'] / stats['total_dreams']) * 100:.2f}%" if stats["total_dreams"] > 0 else "N/A", inline=False)
        embed.add_field(name="Rêve le plus long (en mots)", value=f"{len(stats['longest_dream']['content'].split())} mots: {stats['longest_dream']['title']}" if stats["longest_dream"] else "N/A", inline=False)
        embed.add_field(name="Rêve le plus court (en mots)", value=f"{len(stats['shortest_dream']['content'].split())} mots: {stats['shortest_dream']['title']}" if stats["shortest_dream"] else "N/A", inline=False)
        embed.add_field(name="Nombre de mots total noté sur le serveur", value=stats["total_words"], inline=False)
        embed.add_field(name="Répartition des rêves par jour de la semaine", value=", ".join([f"{day}: {count}" for day, count in zip(['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim'], stats["dreams_per_day_of_week"])]), inline=False)
        embed.add_field(name="Répartition des rêves par mois", value=", ".join([f"{month+1}: {count}" for month, count in enumerate(stats["dreams_per_month"])]), inline=False)

        top_users_text = "\n".join([f"{self.bot.get_user(int(user_id)).display_name}: {len(dreams)} rêves" for user_id, dreams in stats["top_users"]])
        embed.add_field(name="Top 10 des utilisateurs (nombre de rêves)", value=top_users_text, inline=False)

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(DreamJournalStats(bot))
