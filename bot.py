# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

bot_token = os.getenv("DISCORD_BOT_TOKEN")
bot.run(bot_token)

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix='o!', intents=intents, help_command=None)

# Chargement des cogs
initial_extensions = [
    'cogs.welcome',
    'cogs.leave',
    'cogs.wbtb',
    'cogs.reactions',
    'cogs.profile',
    'cogs.stats',
    'cogs.stats2',
    'cogs.stats3',
    'cogs.dreamjournal',
    'cogs.dreamjournal2',  # Ajout du nouveau cog pour les rappels et le calendrier des rêves
    'cogs.dreamjournal3'
    
]

if __name__ == '__main__':
    for extension in initial_extensions:
        bot.load_extension(extension)

@bot.event
async def on_ready():
    print(f'Bot is online as {bot.user}')

@bot.command()
async def help(ctx, *args):
    help_embed = discord.Embed(title="Commandes d'Onyx Bot", color=discord.Color.green())
    help_embed.set_thumbnail(url=bot.user.avatar_url)
    help_embed.set_footer(text="Tapez o!help <command> pour plus de détails sur chaque commande.")

    if not args:
        help_embed.add_field(name="DreamJournal:", value="Pour ceux qui veulent se souvenir de leurs rêves et pas juste dormir comme une souche.", inline=False)
        help_embed.add_field(name="`adddream`", value="Ajoutez un rêve. Ne vous attendez pas à un Oscar.", inline=True)
        help_embed.add_field(name="`deletedream`", value="Supprimez un rêve. Oui, faites comme si ça n'était jamais arrivé.", inline=True)
        help_embed.add_field(name="`listdreams`", value="Listez vos rêves. Voyons si vous avez une imagination.", inline=True)
        help_embed.add_field(name="`searchdreams`", value="Cherchez un rêve. Parce que parfois, Google ne suffit pas.", inline=True)
        help_embed.add_field(name="`viewdream`", value="Voyez un rêve en détail. Préparez-vous à l'ennui.", inline=True)
        help_embed.add_field(name="`dreamcalendar`", value="Affiche un calendrier des rêves. Pour voir vos nuits en couleur.", inline=True)
        help_embed.add_field(name="`userdreamstats`", value="Affiche vos statistiques de rêves. Parce que les chiffres sont importants.", inline=True)
        help_embed.add_field(name="`generaldreamstats`", value="Affiche les statistiques générales de tous les rêves. Pour les obsédés des stats.", inline=True)

        help_embed.add_field(name="Profile:", value="Parce que tout le monde mérite de se la péter avec ses rêves lucides.", inline=False)
        help_embed.add_field(name="`addrl`", value="Ajoutez des RL. Parce que rêver, c'est vivre.", inline=True)
        help_embed.add_field(name="`profile`", value="Voyez votre profil. Votre vie en résumé.", inline=True)
        help_embed.add_field(name="`setrl`", value="Définissez le nombre de RL. Ne trichez pas, on vous voit.", inline=True)

        help_embed.add_field(name="Stats:", value="Pour ceux qui aiment les chiffres plus que les rêves.", inline=False)
        help_embed.add_field(name="`mystats`", value="Vos stats personnelles. Spoiler : elles sont mauvaises.", inline=True)
        help_embed.add_field(name="`rank`", value="Classement des utilisateurs. Voyons qui est le plus bavard.", inline=True)

        help_embed.add_field(name="WBTB:", value="Pour les warriors du sommeil interrompu.", inline=False)
        help_embed.add_field(name="`wbtb`", value="Définissez une alarme WBTB. Debout, feignasse !", inline=True)
        help_embed.add_field(name="`wbtblist`", value="Listez vos alarmes WBTB. Histoire de savoir quand vous réveiller.", inline=True)

        help_embed.add_field(name="No Category:", value="Commandes diverses pour les curieux.", inline=False)
        help_embed.add_field(name="`help`", value="Montre ce message. Sérieusement, encore besoin d'aide ?", inline=True)

    elif len(args) == 1:
        command = bot.get_command(args[0])
        if command:
            descriptions = {
                "adddream": """Ajoutez un rêve à votre journal. 
Utilisation: `o!adddream`
Le bot vous guidera pour enregistrer le titre et le contenu de votre rêve. 
Parfait pour les écrivains en herbe ou les rêveurs obsessionnels.""",

                "deletedream": """Supprimez un rêve de votre journal. 
Utilisation: `o!deletedream <titre>`
Effacez les traces de vos moments les plus embarrassants. 
Assurez-vous de bien orthographier le titre pour éviter les catastrophes.""",

                "listdreams": """Listez tous vos rêves enregistrés. 
Utilisation: `o!listdreams`
Voyons si vous êtes plus Shakespeare ou série Z. 
Affiche le titre et la date de chaque rêve.""",

                "searchdreams": """Cherchez un rêve spécifique dans votre journal. 
Utilisation: `o!searchdreams <mot-clé>`
Parce que même Freud aurait besoin d'aide pour trouver vos rêves. 
Recherche les rêves par titre ou contenu.""",

                "viewdream": """Voyez un rêve en détail. 
Utilisation: `o!viewdream <titre>`
Plongez dans votre subconscient, mais n'oubliez pas de revenir. 
Affiche le titre, le contenu, et la date du rêve.""",

                "dreamcalendar": """Affiche un calendrier des rêves. 
Utilisation: `o!dreamcalendar`
Voyez vos nuits en couleur avec un beau calendrier de vos rêves notés.""",

                "userdreamstats": """Affichez vos statistiques de rêves. 
Utilisation: `o!userdreamstats [@membre]`
Découvrez combien de rêves vous avez notés, combien sont lucides, et plus encore. 
Affiche des statistiques détaillées pour l'utilisateur spécifié.""",

                "generaldreamstats": """Affichez les statistiques générales de tous les rêves. 
Utilisation: `o!generaldreamstats`
Voyez combien de rêves ont été notés sur le serveur, le top 10 des utilisateurs, et plus encore. 
Affiche des statistiques détaillées pour tous les utilisateurs.""",

                "addrl": """Ajoutez des rêves lucides à votre profil. 
Utilisation: `o!addrl <nombre>`
Montrez à tout le monde que vous maîtrisez l'art du rêve conscient. 
Les nombres négatifs ne sont pas acceptés.""",

                "profile": """Affichez votre profil onirique. 
Utilisation: `o!profile [@membre]`
Découvrez combien vous êtes impressionnant... ou pas. 
Affiche votre pseudonyme, statut, avatar, nombre de RL et grade onirique.""",

                "setrl": """Définissez le nombre de rêves lucides sur votre profil. 
Utilisation: `o!setrl <nombre>`
Trichez si vous voulez, mais on finira par le savoir. 
Les nombres négatifs ne sont pas acceptés.""",

                "mystats": """Affichez vos statistiques personnelles. 
Utilisation: `o!mystats`
Préparez-vous à être déçu par vos propres chiffres. 
Affiche le nombre de messages sur les dernières 24h, 7j et 30j, ainsi que l'évolution.""",

                "rank": """Affichez le classement des utilisateurs les plus actifs. 
Utilisation: `o!rank`
Qui est le roi des bavards ? 
Affiche le top 10 des utilisateurs avec leur nombre de messages et l'évolution.""",

                "wbtb": """Définissez une alarme pour vous réveiller en pleine nuit. 
Utilisation: `o!wbtb <heure>`
Parfait pour les adeptes du Wake Back To Bed. 
Supporte les formats 24h et 12h avec am/pm.""",

                "wbtblist": """Listez toutes vos alarmes WBTB. 
Utilisation: `o!wbtblist`
Planifiez vos réveils nocturnes avec précision. 
Affiche l'heure de chaque alarme.""",

                "help": """Affiche ce message d'aide. 
Utilisation: `o!help [commande]`
Sérieusement, tu as encore besoin d'aide ?
Affiche la liste des commandes ou la description d'une commande spécifique."""
            }
            help_embed.title = f"Commande `{command}`"
            help_embed.description = descriptions.get(args[0], "Pas de description disponible.")
        else:
            help_embed.description = f"Commande `{args[0]}` non trouvée. Peut-être que tu rêves trop."

    await ctx.send(embed=help_embed)
