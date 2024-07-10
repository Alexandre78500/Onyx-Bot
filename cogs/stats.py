import discord
from discord.ext import commands
from datetime import datetime, timedelta, timezone
import json
import os

dreams_file = "data/dreams.json"

class Stats(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        # Charger les données depuis le fichier JSON pour les rêves
        if os.path.exists(dreams_file):
            with open(dreams_file, 'r') as f:
                self.dreams = json.load(f)
        else:
            self.dreams = {}

        self.combo_reset_hour = 3
        self.timezone = timezone(timedelta(hours=2))

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

    def format_growth(self, growth):
        if growth == float('inf'):
            return "∞%"
        color = "green" if growth >= 0 else "red"
        sign = "+" if growth >= 0 else ""
        return f"```diff\n{sign}{growth:.2f}%```"

def setup(bot):
    bot.add_cog(Stats(bot))
