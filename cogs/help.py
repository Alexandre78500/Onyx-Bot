import discord
from discord.ext import commands
import asyncio

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = discord.Color.purple()  # Couleur thématique pour les embeds

    @commands.command()
    async def help(self, ctx, *args):
        if not args:
            await self.send_paginated_help(ctx)
        elif len(args) == 1:
            await self.send_command_help(ctx, args[0])

    async def send_paginated_help(self, ctx):
        pages = self.create_help_pages()
        current_page = 0

        message = await ctx.send(embed=pages[current_page])
        await message.add_reaction('⬅️')
        await message.add_reaction('➡️')
        await message.add_reaction('❌')

        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ['⬅️', '➡️', '❌']

        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)

                if str(reaction.emoji) == '➡️' and current_page < len(pages) - 1:
                    current_page += 1
                elif str(reaction.emoji) == '⬅️' and current_page > 0:
                    current_page -= 1
                elif str(reaction.emoji) == '❌':
                    await message.delete()
                    return

                await message.edit(embed=pages[current_page])
                await message.remove_reaction(reaction, user)

            except asyncio.TimeoutError:
                await message.clear_reactions()
                break

    def create_help_pages(self):
        pages = []
        commands_per_page = 4
        all_commands = [
            ("📓 Journal des Rêves", [
                ("interactivedream", "Gestion interactive de vos rêves"),
                ("dreamcalendar", "Calendrier de vos rêves"),
                ("dstats", "Vos statistiques de rêves"),
                ("gstats", "Statistiques globales des rêves")
            ]),
            ("👤 Profil", [
                ("addrl", "Ajouter des rêves lucides"),
                ("profile", "Voir votre profil onirique"),
                ("setrl", "Définir le nombre de rêves lucides")
            ]),
            ("📊 Statistiques", [
                ("mystats", "Vos statistiques personnelles"),
                ("rank", "Classement des utilisateurs")
            ]),
            ("⏰ WBTB", [
                ("wbtb", "Définir une alarme WBTB"),
                ("wbtblist", "Liste de vos alarmes WBTB")
            ]),
            ("💡 Idées", [
                ("submitidea", "Soumettre une idée"),
            ]),
            ("🛠️ Admin", [
                ("listideas", "Lister les idées (admin)"),
                ("relay", "Relayer un message (admin)")
            ]),
            ("❓ Aide", [
                ("help", "Afficher ce message d'aide")
            ])
        ]

        for i in range(0, len(all_commands), commands_per_page):
            embed = discord.Embed(
                title="Guide des Commandes Onyx Bot",
                description=f"Page {i//commands_per_page + 1}/{-(-len(all_commands)//commands_per_page)}",
                color=self.color
            )
            embed.set_thumbnail(url=self.bot.user.avatar_url)
            embed.set_footer(text="Utilisez o!help <commande> pour plus de détails")

            for category, commands in all_commands[i:i+commands_per_page]:
                value = "\n".join([f"`o!{cmd}` • {desc}" for cmd, desc in commands])
                embed.add_field(name=category, value=value, inline=False)

            pages.append(embed)

        return pages

    async def send_command_help(self, ctx, command_name):
        command = self.bot.get_command(command_name)
        if command:
            embed = discord.Embed(title=f"Commande : {command}", color=self.color)
            embed.set_thumbnail(url=self.bot.user.avatar_url)
            description = self.get_command_description(command_name)
            embed.description = f"```{description}```"
            embed.set_footer(text="Syntax: <> = obligatoire, [] = optionnel")
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"😕 La commande `{command_name}` n'existe pas. Essayez `o!help` pour voir toutes les commandes.")

    def get_command_description(self, command_name):
        descriptions = {
            "interactivedream": """Gestion interactive de vos rêves.
Utilisation: o!interactivedream
Navigation par réactions pour gérer vos rêves :
- Ajouter un nouveau rêve
- Lister vos rêves
- Visualiser un rêve spécifique
- Supprimer un rêve
- Rechercher dans vos rêves""",

            "dreamcalendar": """Affiche un calendrier de vos rêves.
Utilisation: o!dreamcalendar
Visualisez vos rêves sur un calendrier coloré.""",

            "dstats": """Statistiques de vos rêves.
Utilisation: o!dstats [@membre]
Affiche des statistiques détaillées sur vos rêves ou ceux d'un autre membre.""",

            "gstats": """Statistiques globales des rêves.
Utilisation: o!gstats
Affiche des statistiques sur tous les rêves enregistrés sur le serveur.""",

            "addrl": """Ajoute des rêves lucides à votre profil.
Utilisation: o!addrl <nombre>
Mettez à jour votre compteur de rêves lucides.""",

            "profile": """Affiche votre profil onirique.
Utilisation: o!profile [@membre]
Voir votre profil ou celui d'un autre membre.""",

            "setrl": """Définit le nombre total de rêves lucides.
Utilisation: o!setrl <nombre>
Réinitialisez votre compteur de rêves lucides.""",

            "mystats": """Affiche vos statistiques d'activité.
Utilisation: o!mystats
Voir votre activité sur les derniers 24h, 7j et 30j.""",

            "rank": """Classement des utilisateurs les plus actifs.
Utilisation: o!rank
Affiche le top 10 des membres les plus actifs.""",

            "wbtb": """Définit une alarme Wake Back To Bed.
Utilisation: o!wbtb <heure>
Planifiez votre réveil pour la technique WBTB.""",

            "wbtblist": """Liste vos alarmes WBTB.
Utilisation: o!wbtblist
Affiche toutes vos alarmes WBTB programmées.""",

            "submitidea": """Soumettez une idée pour le bot.
Utilisation: o!submitidea <votre idée>
Partagez vos suggestions d'amélioration.""",

            "listideas": """Liste toutes les idées soumises.
Utilisation: o!listideas
Réservé à l'administrateur.""",

            "relay": """Relaye un message vers un canal spécifique.
Utilisation: o!relay <message>
Réservé à l'administrateur.""",

            "help": """Affiche l'aide du bot.
Utilisation: o!help [commande]
Sans argument, montre la liste des commandes.
Avec une commande, affiche les détails de celle-ci."""
        }
        return descriptions.get(command_name, "Description non disponible.")

def setup(bot):
    bot.add_cog(Help(bot))