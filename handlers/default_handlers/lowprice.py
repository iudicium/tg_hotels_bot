from telebot.types import Message
from states.all_states import UserData
from loader import bot
from datetime import datetime
from loader import logger
@bot.message_handler(commands=["lowprice"])
def low_price(message: Message):
    time_now = datetime.now().replace(second=0, microsecond=0)
    logger.info("USER CALLED /LOWPRICE COMMAND")

    bot.set_state(message.from_user.id, UserData.city, message.chat.id)
    bot.send_message(message.from_user.id, text=f"Good evening!\nPlease enter the city in which you would like to search hotels for.")
    price_object = {"price": {"max": 250, "min": 50}}
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["command"] = "/lowprice"
        data["filter"] = "PRICE_LOW_TO_HIGH"
        data["date_of_command"] = time_now
        data["price"] = price_object




