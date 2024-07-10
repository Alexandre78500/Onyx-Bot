import discord
from discord.ext import commands
import re
from datetime import datetime, timedelta
import random

class Reactions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.gm_count = 0
        self.last_gm_reset = datetime.utcnow()
        self.gm_sent_today = False

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

def setup(bot):
    bot.add_cog(Reactions(bot))
