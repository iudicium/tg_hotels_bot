from os import getenv
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit('We cannot load the bot due to the .env file not existing.')
else:
    load_dotenv()

API_HOST = "hotels4.p.rapidapi.com"
BOT_TOKEN = getenv('BOT_TOKEN')
RAPID_API_KEY = getenv('RAPID_API_KEY')
DEFAULT_COMMANDS = (
    ('start', "Start the bot"),
    ('help', "Send the commands"),
    ("lowprice", "Searching for hotels with lower price"),
    ("highprice", "Searching for hotels with higher price"),
    ("bestdeal", "Best deal about hotels"),
    ("history", "Sending commands and hotels that were found."),
    ("cancel", "Cancel current command.")
)

