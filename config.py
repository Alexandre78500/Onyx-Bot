# config.py
import os
from dotenv import load_dotenv

load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

INITIAL_EXTENSIONS = [
    'dreamjournal',
    'profile',
    'statistics',
    'utilities',
    'admin',
    'fun',
    'help',
    'leave',
    'welcome',
    'contextual_help'
]

# Autres configurations globales ici
