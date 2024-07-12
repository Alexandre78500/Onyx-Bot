# cogs/admin.py
import discord
from discord.ext import commands
import json
import os

ideas_file = "data/ideas.json"

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        if os.path.exists(ideas_file):
            with open(ideas_file, 'r') as f:
                self.ideas = json.load(f)
        else:
            self.ideas = {}

    def save_ideas(self):
        with open(ideas_file, 'w') as f:
            json.dump(self.ideas, f, indent=4)

    @commands.command()
    async def listideas(self, ctx):
        """Lister toutes les idées soumises"""
        if ctx.author.name != "pikimi":
            await ctx.send("Vous n'avez pas la permission d'utiliser cette commande.")
            return

        if not self.ideas:
            await ctx.send("Aucune idée n'a été soumise pour le moment.")
            return

        embed = discord.Embed(title="Liste des idées soumises", color=discord.Color.blue())
        for user_id, ideas in self.ideas.items():
            user = await self.bot.fetch_user(int(user_id))
            idea_text = "\n".join(ideas)
            embed.add_field(name=user.name, value=idea_text, inline=False)

        await ctx.send(embed=embed)

    @commands.command()
    async def relay(self, ctx, *, message: str):
        """Relayer un message vers un canal spécifique"""
        if ctx.author.name != "pikimi":
            await ctx.send("Vous n'avez pas la permission d'utiliser cette commande.")
            return

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
    bot.add_cog(Admin(bot))