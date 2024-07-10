# -*- coding: utf-8 -*-

import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import logging
from logging.handlers import RotatingFileHandler

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
log_formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
logFile = 'bot.log'

my_handler = RotatingFileHandler(logFile, mode='a', maxBytes=5*1024*1024,
                                 backupCount=2, encoding=None, delay=0)
my_handler.setFormatter(log_formatter)
my_handler.setLevel(logging.INFO)

app_log = logging.getLogger('root')
app_log.setLevel(logging.INFO)

app_log.addHandler(my_handler)

# Exemple d'utilisation de logging
app_log.info('Bot is starting up...')

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
    'cogs.help'  # Ajout du nouveau cog pour la commande help
]

if __name__ == '__main__':
    for extension in initial_extensions:
        try:
            bot.load_extension(extension)
            app_log.info(f'Successfully loaded extension {extension}')
        except Exception as e:
            app_log.error(f'Failed to load extension {extension}.', exc_info=True)

@bot.event
async def on_ready():
    app_log.info(f'Bot is online as {bot.user}')

@bot.event
async def on_command_error(ctx, error):
    app_log.error(f'Error in command {ctx.command}: {error}', exc_info=True)

bot.run(bot_token)
