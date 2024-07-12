# cogs/fun.py
import discord
from discord.ext import commands
import re
from datetime import datetime, timedelta
import random
import json
import os

ideas_file = "data/ideas.json"

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.gm_count = 0
        self.last_gm_reset = datetime.utcnow()
        self.gm_sent_today = False
        if os.path.exists(ideas_file):
            with open(ideas_file, 'r') as f:
                self.ideas = json.load(f)
        else:
            self.ideas = {}

    def save_ideas(self):
        with open(ideas_file, 'w') as f:
            json.dump(self.ideas, f, indent=4)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author == self.bot.user:
            return

        # Réaction hap
        if ":hap:" in message.content:
            hap_emoji = discord.utils.get(message.guild.emojis, name='hap')
            if hap_emoji:
                await message.add_reaction(hap_emoji)
            else:
                print("Emoji :hap: non trouvé sur le serveur")

        # Réaction noel
        if ":noel:" in message.content:
            noel_emoji = discord.utils.get(message.guild.emojis, name='noel')
            if noel_emoji:
                await message.add_reaction(noel_emoji)
            else:
                print("Emoji :noel: non trouvé sur le serveur")

        # Réaction gm
        now = datetime.utcnow()
        if (now - self.last_gm_reset) > timedelta(days=1):
            self.gm_count = 0
            self.last_gm_reset = now
            self.gm_sent_today = False

        if re.search(r'\bgm\b', message.content, re.IGNORECASE):
            self.gm_count += 1
            if self.gm_count <= 2 and not self.gm_sent_today:  # Limite de 1 réponse par jour, aléatoire sur les 2 premiers messages
                if random.choice([True, False]):
                    await message.channel.send(random.choice(['gm', 'Gm', 'GM']))
                    self.gm_sent_today = True

    @commands.command()
    async def submitidea(self, ctx, *, idea: str):
        """Soumettre une idée pour améliorer le bot"""
        user_id = str(ctx.author.id)
        if user_id not in self.ideas:
            self.ideas[user_id] = []
        self.ideas[user_id].append(idea)
        self.save_ideas()
        await ctx.send(f"Merci pour votre idée, {ctx.author.mention} ! Elle a bien été enregistrée.")

def setup(bot):
    bot.add_cog(Fun(bot))