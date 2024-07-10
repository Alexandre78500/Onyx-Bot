import discord
from discord.ext import commands
import json
import os

data_file = "data/user_data.json"

if not os.path.exists("data"):
    os.makedirs("data")

# Charger les données depuis le fichier JSON
if os.path.exists(data_file):
    with open(data_file, 'r') as f:
        user_data = json.load(f)
else:
    user_data = {}

grades = [
    (0, "Néant"),
    (1, "Lueur Onirique"),
    (3, "Commencement Onirique"),
    (5, "Débutant Onirique"),
    (10, "Apprenti Onironaute"),
    (15, "Jeune Onironaute"),
    (20, "Soldat Onironaute"),
    (30, "Mage Onironaute"),
    (40, "Mage avancé Onironaute"),
    (50, "Forgeron onirique"),
    (60, "Centurion Onirique"),
    (80, "Archimage Onirique"),
    (100, "Maître Onironaute"),
    (150, "Ascète Onirique"),
    (200, "Créature onirique"),
    (300, "Morphée")
]

def get_user_grade(rl_count):
    grade = "Néant"
    for rl, gr in grades:
        if rl_count >= rl:
            grade = gr
        else:
            break
    return grade

def save_user_data():
    with open(data_file, 'w') as f:
        json.dump(user_data, f)

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def update_roles(self, member, new_grade):
        guild = member.guild
        # Enlever tous les anciens rôles de grade
        for rl, grade in grades:
            role = discord.utils.get(guild.roles, name=grade)
            if role in member.roles:
                await member.remove_roles(role)
        
        # Ajouter le nouveau rôle
        new_role = discord.utils.get(guild.roles, name=new_grade)
        if new_role:
            await member.add_roles(new_role)

    @commands.command()
    async def profile(self, ctx, member: discord.Member = None):
        if member is None:
            member = ctx.author

        pseudonyme = member.name
        status = member.status
        avatar_url = str(member.avatar_url)

        user_info = user_data.get(str(member.id), {'rl_count': 0})
        rl_count = user_info['rl_count']
        grade = get_user_grade(rl_count)

        if status == discord.Status.online:
            status_text = "Online"
        elif status == discord.Status.offline:
            status_text = "Offline"
        elif status == discord.Status.idle:
            status_text = "Idle"
        elif status == discord.Status.dnd:
            status_text = "Do Not Disturb"
        else:
            status_text = "Unknown"

        embed = discord.Embed(title=f"Profil de {pseudonyme}", color=discord.Color.blue())
        embed.set_thumbnail(url=avatar_url)
        embed.add_field(name="Pseudonyme", value=pseudonyme, inline=True)
        embed.add_field(name="Statut", value=status_text, inline=True)
        embed.add_field(name="Nombre de RL", value=rl_count, inline=True)
        embed.add_field(name="Grade Onirique", value=grade, inline=True)
        
        await ctx.send(embed=embed)

    @commands.command()
    async def addrl(self, ctx, n: int):
        user = ctx.author
        pseudonyme = user.name
        user_id = str(user.id)
        if user_id not in user_data:
            user_data[user_id] = {'rl_count': 0}
        
        new_rl_count = user_data[user_id]['rl_count'] + n
        if new_rl_count < 0:
            await ctx.send(f"{pseudonyme}, vous ne pouvez pas avoir un nombre de RL négatif. C'est pas bien !")
        else:
            user_data[user_id]['rl_count'] = new_rl_count
            save_user_data()  # Sauvegarder les données après modification
            rl_count = user_data[user_id]['rl_count']
            grade = get_user_grade(rl_count)
            await ctx.send(f"{pseudonyme} a maintenant {rl_count} RL et le grade de {grade}")
            
            # Mettre à jour les rôles
            await self.update_roles(ctx.author, grade)

    @commands.command()
    async def setrl(self, ctx, n: int):
        user = ctx.author
        pseudonyme = user.name
        user_id = str(user.id)
        if n < 0:
            await ctx.send(f"{pseudonyme}, vous ne pouvez pas avoir un nombre de RL négatif. C'est pas bien !")
        else:
            user_data[user_id] = {'rl_count': n}
            save_user_data()  # Sauvegarder les données après modification
            rl_count = user_data[user_id]['rl_count']
            grade = get_user_grade(rl_count)
            await ctx.send(f"{pseudonyme} a maintenant {rl_count} RL et le grade de {grade}")
            
            # Mettre à jour les rôles
            await self.update_roles(ctx.author, grade)

    async def add_rl(self, member: discord.Member):
        user_id = str(member.id)
        if user_id not in user_data:
            user_data[user_id] = {'rl_count': 0}
        
        user_data[user_id]['rl_count'] += 1
        save_user_data()

        # Mettre à jour le rôle de l'utilisateur en fonction du grade
        rl_count = user_data[user_id]['rl_count']
        grade = get_user_grade(rl_count)
        await self.update_roles(member, grade)

def setup(bot):
    bot.add_cog(Profile(bot))
