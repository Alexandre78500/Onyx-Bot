# bot.py

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import logging
from logging_config import log_command

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

bot_token = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix='o!', intents=intents, help_command=None)

# Configurer le logging
logger = logging.getLogger('bot')
logger.setLevel(logging.INFO)

# Exemple d'utilisation de logging
logger.info('Bot is starting up...')

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
    'cogs.dreamjournal2',
    'cogs.dreamjournal3',
    'cogs.help',
    'cogs.ideas',
    'cogs.relay',
    'cogs.contextual_help'  # Ajout du nouveau cog pour l'aide contextuelle
]

if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
            logger.info(f'Successfully loaded extension {extension}')
        except Exception as e:
            logger.error(f'Failed to load extension {extension}.', exc_info=True)

@bot.event
async def on_ready():
    logger.info(f'Bot is online as {bot.user}')

@bot.event
async def on_command_error(ctx, error):
    if hasattr(ctx.command, 'on_error'):
        return
    
    cog = ctx.cog
    if cog and cog._get_overridden_method(cog.cog_command_error) is not None:
        return

    ignored = (commands.CommandNotFound, commands.MissingRequiredArgument, commands.BadArgument)
    error = getattr(error, 'original', error)

    if isinstance(error, ignored):
        return

    if isinstance(error, commands.DisabledCommand):
        await ctx.send(f'{ctx.command} a été désactivée.')
    elif isinstance(error, commands.NoPrivateMessage):
        try:
            await ctx.author.send(f'{ctx.command} ne peut pas être utilisée dans les messages privés.')
        except discord.HTTPException:
            pass
    else:
        logger.error(f'Error in command {ctx.command}: {error}', exc_info=True)
        await ctx.send("Une erreur inattendue est survenue. L'équipe technique a été notifiée.")

@bot.event
async def on_command(ctx):
    logger.info(f"Command '{ctx.command}' executed by user '{ctx.author}'")
    log_command(ctx.command.name, ctx.author)

bot.run(bot_token)