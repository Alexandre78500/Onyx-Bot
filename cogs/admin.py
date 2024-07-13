# cogs/admin.py
import discord
from discord.ext import commands
import json
import os
import math

ideas_file = "data/ideas.json"

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.load_ideas()

    def load_ideas(self):
        if os.path.exists(ideas_file):
            with open(ideas_file, 'r') as f:
                self.ideas = json.load(f)
        else:
            self.ideas = {"pending": {}, "later": {}, "completed": {}, "rejected": {}}
        
        # Check for old format and migrate
        if not any(k in self.ideas for k in ['pending', 'later', 'completed', 'rejected']):
            self.ideas = {"pending": self.ideas, "later": {}, "completed": {}, "rejected": {}}
            self.save_ideas()

    def save_ideas(self):
        with open(ideas_file, 'w') as f:
            json.dump(self.ideas, f, indent=4)

    @commands.command()
    async def listideas(self, ctx, category: str = "pending"):
        """Lister toutes les idées soumises"""
        if ctx.author.name != "pikimi":
            await ctx.send("Vous n'avez pas la permission d'utiliser cette commande.")
            return

        if category not in self.ideas or not self.ideas[category]:
            await ctx.send(f"Aucune idée dans la catégorie '{category}'.")
            return

        await self.send_paginated_ideas(ctx, category)

    async def send_paginated_ideas(self, ctx, category):
        ideas_per_page = 5
        ideas_list = [(user_id, idea) for user_id, ideas in self.ideas[category].items() for idea in ideas]
        total_pages = math.ceil(len(ideas_list) / ideas_per_page)
        current_page = 0

        embed = self.create_ideas_embed(ctx, ideas_list, category, current_page, total_pages, ideas_per_page)
        message = await ctx.send(embed=embed)
        await message.add_reaction('⬅️')
        await message.add_reaction('➡️')
        await message.add_reaction('❌')
        await message.add_reaction('✅')  # Completed
        await message.add_reaction('📤')  # Later
        await message.add_reaction('❌')  # Rejected
        await message.add_reaction('🗑️')  # Delete

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['⬅️', '➡️', '❌', '✅', '📤', '🗑️']

        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)

                if str(reaction.emoji) == '➡️' and current_page < total_pages - 1:
                    current_page += 1
                elif str(reaction.emoji) == '⬅️' and current_page > 0:
                    current_page -= 1
                elif str(reaction.emoji) == '❌':
                    await message.delete()
                    return
                elif str(reaction.emoji) == '✅':
                    await self.move_idea(ctx, ideas_list, category, current_page, ideas_per_page, 'completed')
                elif str(reaction.emoji) == '📤':
                    await self.move_idea(ctx, ideas_list, category, current_page, ideas_per_page, 'later')
                elif str(reaction.emoji) == '🗑️':
                    await self.delete_idea(ctx, ideas_list, category, current_page, ideas_per_page)

                embed = self.create_ideas_embed(ctx, ideas_list, category, current_page, total_pages, ideas_per_page)
                await message.edit(embed=embed)
                await message.remove_reaction(reaction, user)

            except asyncio.TimeoutError:
                await message.clear_reactions()
                break

    def create_ideas_embed(self, ctx, ideas_list, category, page, total_pages, ideas_per_page):
        embed = discord.Embed(
            title=f"Liste des idées ({category}) - Page {page + 1}/{total_pages}",
            color=discord.Color.blue()
        )
        start_index = page * ideas_per_page
        end_index = start_index + ideas_per_page
        for user_id, idea in ideas_list[start_index:end_index]:
            user = self.bot.get_user(int(user_id))
            embed.add_field(name=user.name, value=idea, inline=False)

        embed.set_footer(text=f"Utilisez les réactions pour naviguer • Page {page + 1}/{total_pages}")
        return embed

    async def move_idea(self, ctx, ideas_list, category, current_page, ideas_per_page, new_category):
        start_index = current_page * ideas_per_page
        end_index = start_index + ideas_per_page
        selected_idea = ideas_list[start_index:end_index][0]
        user_id, idea = selected_idea

        self.ideas[category][str(user_id)].remove(idea)
        if not self.ideas[category][str(user_id)]:
            del self.ideas[category][str(user_id)]
        self.ideas[new_category].setdefault(str(user_id), []).append(idea)
        self.save_ideas()
        await ctx.send(f"Idée déplacée vers '{new_category}'.")

    async def delete_idea(self, ctx, ideas_list, category, current_page, ideas_per_page):
        start_index = current_page * ideas_per_page
        end_index = start_index + ideas_per_page
        selected_idea = ideas_list[start_index:end_index][0]
        user_id, idea = selected_idea

        self.ideas[category][str(user_id)].remove(idea)
        if not self.ideas[category][str(user_id)]:
            del self.ideas[category][str(user_id)]
        self.save_ideas()
        await ctx.send("Idée supprimée avec succès.")

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
