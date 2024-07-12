# cogs/profile.py
import discord
from discord.ext import commands
from utils.json_manager import JsonManager

data_file = "data/user_data.json"

grades = [
    (0, "Néant"),
    (1, "Lueur Onirique"),
    (3, "Commencement Onirique"),
    (5, "Débutant Onironaute"),
    (10, "Apprenti Onironaute"),
    (15, "Jeune Onironaute"),
    (20, "Soldat Onironaute"),
    (30, "Mage Onironaute"),
    (40, "Mage Avancé Onironaute"),
    (50, "Forgeron Onironaute"),
    (60, "Centurion Onironaute"),
    (80, "Archimage Onironaute"),
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

class Profile(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.user_data = JsonManager.load_json(data_file, default={})

    def save_user_data(self):
        JsonManager.save_json(data_file, self.user_data)

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

        user_info = self.user_data.get(str(member.id), {'rl_count': 0})
        rl_count = user_info['rl_count']
        grade = get_user_grade(rl_count)

        status_text = {
            discord.Status.online: "Online",
            discord.Status.offline: "Offline",
            discord.Status.idle: "Idle",
            discord.Status.dnd: "Do Not Disturb"
        }.get(status, "Unknown")

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
        if user_id not in self.user_data:
            self.user_data[user_id] = {'rl_count': 0}
        
        new_rl_count = self.user_data[user_id]['rl_count'] + n
        if new_rl_count < 0:
            await ctx.send(f"{pseudonyme}, vous ne pouvez pas avoir un nombre de RL négatif. C'est pas bien !")
        else:
            self.user_data[user_id]['rl_count'] = new_rl_count
            self.save_user_data()
            rl_count = self.user_data[user_id]['rl_count']
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
            self.user_data[user_id] = {'rl_count': n}
            self.save_user_data()
            rl_count = self.user_data[user_id]['rl_count']
            grade = get_user_grade(rl_count)
            await ctx.send(f"{pseudonyme} a maintenant {rl_count} RL et le grade de {grade}")
            
            # Mettre à jour les rôles
            await self.update_roles(ctx.author, grade)

    async def add_rl(self, member: discord.Member):
        user_id = str(member.id)
        if user_id not in self.user_data:
            self.user_data[user_id] = {'rl_count': 0}
        
        self.user_data[user_id]['rl_count'] += 1
        self.save_user_data()

        # Mettre à jour le rôle de l'utilisateur en fonction du grade
        rl_count = self.user_data[user_id]['rl_count']
        grade = get_user_grade(rl_count)
        await self.update_roles(member, grade)

def setup(bot):
    bot.add_cog(Profile(bot))