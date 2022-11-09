from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from config_data import config
from loguru import logger
from sys import stderr
logger.add(stderr, format="{time} {level} {message}", filter="my_module", level="INFO")

storage = StateMemoryStorage()
bot = TeleBot(token=config.BOT_TOKEN, state_storage=storage)

