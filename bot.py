# bot.py
import discord
from discord.ext import commands
from config import DISCORD_BOT_TOKEN, INITIAL_EXTENSIONS
import logging
from logging_config import log_command

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix='o!', intents=intents, help_command=None)

# Configurer le logging
logger = logging.getLogger('bot')
logger.setLevel(logging.INFO)

logger.info('Bot is starting up...')

if __name__ == '__main__':
    for extension in INITIAL_EXTENSIONS:
        try:
            bot.load_extension(f'cogs.{extension}')
            logger.info(f'Successfully loaded extension {extension}')
        except Exception as e:
            logger.error(f'Failed to load extension {extension}.', exc_info=True)

@bot.event
async def on_ready():
    logger.info(f'Bot is online as {bot.user}')

@bot.event
async def on_command(ctx):
    logger.info(f"Command '{ctx.command}' executed by user '{ctx.author}'")
    log_command(ctx.command.name, ctx.author)

bot.run(DISCORD_BOT_TOKEN)
