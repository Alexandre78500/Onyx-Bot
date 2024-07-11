# cogs/relay.py
import discord
from discord.ext import commands

class Relay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def relay(self, ctx, *, message: str):
        target_guild_id = 376777553945296896  # ID de votre serveur public
        target_channel_id = 376777553945296899  # ID du canal public

        target_guild = self.bot.get_guild(target_guild_id)
        if not target_guild:
            await ctx.send("Serveur cible introuvable.")
            return

        target_channel = target_guild.get_channel(target_channel_id)
        if not target_channel:
            await ctx.send("Canal cible introuvable.")
            return

        await target_channel.send(message)
        await ctx.send("Message relayé avec succès.")

def setup(bot):
    bot.add_cog(Relay(bot))
