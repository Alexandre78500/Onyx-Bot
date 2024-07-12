import logging
import os

LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

LOG_FILE = os.path.join(LOG_DIR, "bot.log")

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,  # Set to INFO to avoid too much detail
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )

# Fonction pour enregistrer les commandes
def log_command(command_name, user):
    logger = logging.getLogger('command_logger')
    logger.info(f"Command '{command_name}' executed by user '{user}' (User ID: {user.id})")
