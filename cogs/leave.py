import discord
from discord.ext import commands
import random

class Leave(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        channel = discord.utils.get(member.guild.text_channels, name='blabla-general')
        if channel:
            leave_messages = [
                f"{member.name} a quitté le serveur. Tant mieux, on avait besoin de moins de négativité ici ! 😡",
                f"{member.name} a quitté le serveur. Une nuisance en moins à gérer. 😠",
                f"{member.name} a décidé de partir. Bon débarras ! 👋",
                f"{member.name} a quitté le navire. Bonne chance ailleurs, tu en auras besoin ! 😒",
                f"{member.name} nous a quittés. Enfin un peu de paix et de tranquillité. 🙄",
                f"{member.name} a déserté. Espérons qu'ils trouvent des gens aussi désespérés ailleurs. 😤",
                f"{member.name} a sauté du bateau. Pas une grande perte ! 🚪",
                f"{member.name} est parti. Finalement, un problème de moins ! 👋",
                f"{member.name} a fait ses valises et est parti. Ne revenez jamais ! 😡",
                f"{member.name} nous a abandonnés. Bon débarras et bonne chance ! 👎"
            ]
            leave_message = random.choice(leave_messages)
            await channel.send(leave_message)

def setup(bot):
    bot.add_cog(Leave(bot))
