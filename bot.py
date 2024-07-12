import discord
from discord.ext import commands
from config import DISCORD_BOT_TOKEN, INITIAL_EXTENSIONS
import logging
from logging_config import log_command, setup_logging

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.reactions = True

bot = commands.Bot(command_prefix='o!', intents=intents, help_command=None)

# Configurer le logging
setup_logging()
logger = logging.getLogger('bot')
logger.setLevel(logging.INFO)  # Set to INFO to avoid too much detail

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
    logger.info(f"Command '{ctx.command}' executed by user '{ctx.author}' (User ID: {ctx.author.id}, Guild: {ctx.guild.name}, Channel: {ctx.channel.name})")
    log_command(ctx.command.name, ctx.author)

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    logger.debug(f"Message from {message.author} in {message.channel.name}: {message.content}")
    await bot.process_commands(message)

@bot.event
async def on_error(event, *args, **kwargs):
    logger.error(f'Error in event {event}', exc_info=True)

bot.run(DISCORD_BOT_TOKEN)
