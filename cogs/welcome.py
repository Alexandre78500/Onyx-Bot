import discord
from discord.ext import commands

class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        channel = discord.utils.get(member.guild.text_channels, name='blabla-general')
        if channel:
            welcome_message = (
                f"Bienvenue {member.mention}!\n\n"
                "Si tu es intéressé par les RL et que tu veux découvrir ton monde onirique, tu as deux choix (liste non exhaustive bien sûr) :\n"
                "🌟 **Suivre le starter pack** trouvé ici : #entrepôt-à-connaissance\n"
                "🌟 **Suivre notre défi onirique** qui s'étale sur 30 jours : chaque jour un défi et vous devrez tous les cumuler au fur et à mesure. Les chances de RL sont assez conséquentes ! Tu peux le trouver ici : #defi-onirique\n\n"
                "Bonne exploration et amuse-toi bien ! 😊"
            )
            await channel.send(welcome_message)

def setup(bot):
    bot.add_cog(Welcome(bot))
