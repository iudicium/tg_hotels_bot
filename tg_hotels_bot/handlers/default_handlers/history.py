from telebot.types import Message

from loader import bot
from database.model_functions.user import UserMethods
from database.model_functions.hotel_data import HotelData_Methods
from urllib3.exceptions import ReadTimeoutError
from requests.exceptions import ReadTimeout
from time import sleep
from loader import logger


@bot.message_handler(commands=["history"])
def low_price(message: Message) -> None:
    logger.info("USER CALLED /HISTORY COMMAND")
    user_check = UserMethods.check_if_user_exists(user_id=message.from_user.id)
    if user_check:
        show_history(user_id=message.from_user.id)
    else:
        bot.send_message(message.from_user.id, "Вы еще не отправляли никаких команд.")


def show_history(user_id: int) -> None:
    user_data = UserMethods.return_user_fields(user_id=user_id)
    for user in user_data:
        try:
            hotel_data = user.hotels_found.split(":")
            for hotel_id in hotel_data:
                hotel = HotelData_Methods.return_hotel_data(property_id=hotel_id)
                msg = f"👁️‍🗨️COMMAND: {user.command}\n" \
                      f"⏱DATE AND TIME: {user.date_of_command}\n" \
                      f"🌎HOTEL NAME: {hotel.get('hotel_name')}\n" \
                      f"🏨ADRESS: {hotel.get('adress')}\n" \
                      f"DISTANCE FROM CENTER: {hotel.get('distance_from_center')}\n" \
                      f"💳PRICE PER NIGHT: {hotel.get('nightly_price')}\n" \
                      f"TOTAL PRICE: {hotel.get('total_price')}\n" \
                      f"⭐REVIEWS SCORE: {hotel.get('reviews_score')}\n" \
                      f"✨TOTAL REVIEWS SCORE: {hotel.get('reviews_total')}\n"
                bot.send_photo(chat_id=user_id, caption=msg, photo=hotel.get("photo_url"))
                sleep(2)
        except (ReadTimeout, ReadTimeoutError):
            sleep(5)
            bot.send_message(chat_id=user_id, text="Ожидайте. Проблемы с серверами телеграмма.")
        except Exception as e:
            logger.exception(e)
            bot.send_message(user_id, f"Произошла ошибка. {e}")
