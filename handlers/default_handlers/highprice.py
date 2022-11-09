from telebot.types import Message
from states.all_states import UserData
from loader import bot
from datetime import datetime
from loader import logger
@bot.message_handler(commands=["highprice"])
def high_price(message: Message) -> None:
    time_now = datetime.now().replace(second=0, microsecond=0)
    logger.info("USER CALLED /highprice COMMAND")

    bot.set_state(message.from_user.id, UserData.city, message.chat.id)
    bot.send_message(message.from_user.id, text=f"Good evening!\nPlease enter the city in which you would like to search hotels for.")
    price_object = {"price": {"max": 1500, "min": 500}}
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["filter"] = "PRICE_HIGH_TO_LOW"
        data["command"] = "/highprice"
        data["date_of_command"] = time_now
        data["price"] = price_object


