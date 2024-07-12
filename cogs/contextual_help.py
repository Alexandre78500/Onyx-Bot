# cogs/contextual_help.py

import discord
from discord.ext import commands
from difflib import get_close_matches

class ContextualHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            await self.suggest_similar_command(ctx, ctx.invoked_with)
        elif isinstance(error, commands.MissingRequiredArgument):
            await self.show_command_usage(ctx, ctx.command)
        elif isinstance(error, commands.BadArgument):
            await self.show_argument_help(ctx, ctx.command, error)

    async def suggest_similar_command(self, ctx, attempted_command):
        command_names = [cmd.name for cmd in self.bot.commands]
        close_matches = get_close_matches(attempted_command, command_names, n=3, cutoff=0.6)
        
        if close_matches:
            suggestions = ", ".join([f"`o!{cmd}`" for cmd in close_matches])
            await ctx.send(f"La commande `o!{attempted_command}` n'existe pas. Vouliez-vous dire : {suggestions} ?")
        else:
            await ctx.send(f"La commande `o!{attempted_command}` n'existe pas. Utilisez `o!help` pour voir la liste des commandes disponibles.")

    async def show_command_usage(self, ctx, command):
        usage = self.get_command_usage(command)
        await ctx.send(f"Il manque des arguments pour la commande `{command.name}`.\nUtilisation correcte :\n```{usage}```")

    async def show_argument_help(self, ctx, command, error):
        usage = self.get_command_usage(command)
        await ctx.send(f"Erreur d'argument pour la commande `{command.name}` : {str(error)}\nUtilisation correcte :\n```{usage}```")

    def get_command_usage(self, command):
        if not command.signature:
            return f"o!{command.name}"
        return f"o!{command.name} {command.signature}"

def setup(bot):
    bot.add_cog(ContextualHelp(bot))