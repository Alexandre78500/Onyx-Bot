import discord
from discord.ext import commands
import os
import json

ideas_file = "data/ideas.json"

class Ideas(commands.Cog):
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
    async def submitidea(self, ctx, *, idea: str):
        """Soumettre une idée pour améliorer le bot"""
        user_id = str(ctx.author.id)
        if user_id not in self.ideas:
            self.ideas[user_id] = []
        self.ideas[user_id].append(idea)
        self.save_ideas()
        await ctx.send(f"Merci pour votre idée, {ctx.author.mention} ! Elle a bien été enregistrée.")

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

def setup(bot):
    bot.add_cog(Ideas(bot))
