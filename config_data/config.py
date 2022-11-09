from os import getenv
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit('Переменные окружения не загружены т.к отсутствует файл .env')
else:
    load_dotenv()

API_HOST = "hotels4.p.rapidapi.com"
BOT_TOKEN = getenv('BOT_TOKEN')
RAPID_API_KEY = getenv('RAPID_API_KEY')
DEFAULT_COMMANDS = (
    ('start', "Запустить бота"),
    ('help', "Вывести справку"),
    ("lowprice", "Поиск отелей с меньшей ценой"),
    ("highprice", "Поиск отелей с более высокой ценой"),
    ("bestdeal", "Бест деал по отелям"),
    ("history", "Вывод комманд и отелей которые были найдены"),
    ("cancel", "Отмена команды.")
)

