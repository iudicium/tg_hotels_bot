from telebot.handler_backends import State, StatesGroup
from telebot.storage import StateMemoryStorage
from keyboards.inline.inline_button import Inline
from keyboards.reply.reply_button import Reply
from telebot.types import  Message, CallbackQuery
from database.model_functions.user import UserMethods
from database.model_functions.hotel_photos import HotelPhotos_methods
from loader import bot
from re import search
from pprint import pprint
from .process_data import ProcessData
from api_parse.parse_api_and_unpack import API
from api_parse.api_utils import API_UTILS
from loader import logger

state_storage = StateMemoryStorage()
API_UTILS = API_UTILS()

class UserData(StatesGroup):
    city = State()
    date = State()
    adults_children = State()
    price = State()
    distance = State()
    photos = State()
    photos_amount = State()
    api_response = State()
    finalize_results = State()
@bot.message_handler(state="*", commands=["cancel"])
def cancel_state(message: Message) -> None:
    bot.send_message(message.from_user.id, "Можете вводить комманду опять.")
    bot.set_state(message.from_user.id, None, message.chat.id)

@bot.message_handler(state=UserData.city)
def city_get(message: Message) -> None:
    logger.info("City Function")
    city, chat_id, from_user_id = message.text, message.chat.id, message.from_user.id


    url, headers = API_UTILS.location_url, API_UTILS.headers
    query_string = {"q": city}
    location_response = API.request_to_api(url=url, headers=headers, query_string=query_string)
    city_data = API.unpack_locationv3_json(json_str=location_response.text, city_group=city)
    if city_data:
        markup = Inline().add_buttons(text=city_data["fullName"], callback=city_data["gaiaId"])
        bot.send_message(chat_id, "Уточните пожалуйста!", reply_markup=markup)

    bot.set_state(from_user_id, UserData.date, chat_id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["city_chosen"] = city


@bot.message_handler(state=UserData.date)
def get_date(message: Message) -> None:
    logger.info("Date Function")
    dates = message.text.split()
    check_date = ProcessData.check_dates_validity(dates=dates)
    if not check_date:
        bot.send_message(message.from_user.id, "Не верный формат даты. Попробуйте еще раз.")
        bot.set_state(message.from_user.id, UserData.date, message.chat.id)

    # with bot.retrieve_data(message.from_user.id, message.chat.id) as user_data:
    #     user_data["date"] = dates
    else:
        ProcessData.save_data(user_id=message.from_user.id, chat_id=message.chat.id, dict_key="date", data=check_date)
        bot.send_message(message.chat.id,
                         "Отлично. Теперь введите сколько взрослых и комнат для детей нужно."
                         "\nФормат: Adults Children\n"
                         "Если больше чем два ребенка разделиите возраст запятой\nПример 1: 2 5,6\n"
                         "Пример 2:  2 (Без детей)")
        bot.set_state(message.from_user.id, UserData.adults_children, message.chat.id)
    # TODO add calendar




@bot.message_handler(state=UserData.adults_children)
def adults_children(message: Message) -> None:
    logger.info("Getting adults")
    adults_children_object = message.text.split()
    pattern = r'[A-Za-z]'
    find = search(pattern, message.text)
    if find:
        bot.send_message(message.from_user.id, "В этом параметре принимаются только цифры и запятые если нужно.\nПопробуйте еще раз.")
        bot.set_state(message.from_user.id, UserData.adults_children, message.chat.id)
    else:
        if len(adults_children_object) == 1:
            adults = adults_children_object[0]
            children_object = list()
        else:
            adults = adults_children_object[0]
            children_object = adults_children_object[1].split(",")
        rooms_object = ProcessData.create_rooms_object(adults=adults, children_ages=children_object)
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            command  = data["command"]
        if command == "/bestdeal":
            bot.set_state(message.from_user.id, UserData.price, message.chat.id)
            bot.send_message(message.from_user.id, "Пожалуйста отправьте минимальную и максимальную цену отеля.\nФормат: Мин Макс(50 100)\nОтправьте 0 для пре установленной цены.")
        else:
            markup = Inline().add_buttons(text=["Да", "Нет"], callback=["photo_yes", "photo_no"])
            bot.send_message(message.from_user.id, "Хотите ли выгружать фото?", reply_markup=markup)
            bot.set_state(message.from_user.id, UserData.photos, message.chat.id)
        ProcessData.save_data(user_id=message.from_user.id, chat_id=message.chat.id,
                              dict_key="adults_children", data=rooms_object)



@bot.message_handler(state=UserData.price)
def get_price(message: Message) -> None:

    logger.info("Getting price")
    pattern = r'[A-Za-z]'
    find = search(pattern, message.text)
    if find:
        bot.send_message(message.from_user.id,
                         "В этом параметре принимаются только цифры.\nПопробуйте еще раз.")
        bot.set_state(message.from_user.id, UserData.adults_children, message.chat.id)
    else:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:

            if data["filter"] == "PRICE_HIGH_TO_LOW" and message.text == "0":
                min_price, max_price = 100, 1500
            elif data["command"] == "/bestdeal" and message.text == "0":
                min_price, max_price = 1, 500
            elif message.text == "0":
                min_price, max_price = 100, 150
            else:
                min_price, max_price = message.text.split()
        price_object = {"price": {"max": max_price, "min": min_price}}
        bot.send_message(chat_id=message.chat.id, text="Введите дистанцию от центра. в км")
        bot.set_state(message.from_user.id, UserData.distance, message.chat.id)
        ProcessData.save_data(user_id=message.from_user.id, chat_id=message.chat.id, dict_key="price", data=price_object)

@bot.message_handler(state=UserData.distance)
def get_distance(message: Message) -> None:
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["filter"] = f"DISTANCE ({message.text})"

    markup = Inline().add_buttons(text=["Да", "Нет"], callback=["photo_yes", "photo_no"])
    bot.send_message(message.from_user.id, "Хотите ли выгружать фото?", reply_markup=markup)
@bot.message_handler(state=UserData.photos_amount)
def photos_amount(message: Message) -> None:
    logger.info("Photos Amount")
    if not message.text.isdigit():
        bot.send_message(message.from_user.id, "Вы должны ввести только цифры на этом этапе. Попробуйте еще раз.")
        bot.set_state(message.from_user.id, UserData.photos_amount, message.chat.id)
    else:
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data["photos_amount"] = int(message.text)

    markup = Reply.add_buttons(text="Начать Поиск")
    bot.send_message(message.chat.id, text="Начнем?", reply_markup=markup)
    bot.set_state(message.from_user.id, UserData.api_response, message.chat.id)

@bot.message_handler(state=UserData.api_response)
def process_data(message: Message) -> None:
    logger.info("Processing data")
    url, headers = API_UTILS.properties_url, API_UTILS.headers
    headers["content-type"] = "application/json"
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        photos_upload = data.get("photos")
        results_number = 500
        sort, city_name, command, date_of_command = data["filter"], data["city_chosen"], data["command"], data["date_of_command"]
        payload = ProcessData.finalize_payload(data=data, sort=sort, result_size=results_number)
        results = API.post_request(url=url, payload=payload, headers=headers)

    if results:
        hotels_founds = API.unpack_propertiesv2_json(response=results, results_amount=results_number,
                                                    city=city_name, photo_upload=photos_upload, user_id=message.from_user.id)
        if hotels_founds:
            UserMethods.create_record(user_id=message.from_user.id, user_name=message.from_user.username,
                               command=command, date_of_command=date_of_command, hotel_ids=hotels_founds)
            bot.send_message(message.chat.id, "Поиск окончен.")
        # if not detailed_results:
        #     bot.send_message(message.from_user.id, "Похоже, что у сервера сейчас проблема. Пожалуйста, напишите автору бота.")
    else:
        bot.send_message(message.from_user.id, "Мы не нашли результатов для ваших параметров. || Это сообщение может возникнуть тоже изза проблем с сервером")
    bot.set_state(message.from_user.id, None, message.chat.id)

""" BUTTON CALLBACKS"""
@bot.callback_query_handler(func=lambda call: call.data.isdigit())
def date_callback(call: CallbackQuery) -> None:

    logger.info("Extra city callback")
    if call.data.isdigit():
        with bot.retrieve_data(call.from_user.id, call.from_user.id) as data:
            data["city"] = call.data
        bot.send_message(call.from_user.id,
                         'Теперь, отправьте, дату check in и checkout в отель.\nФормат:  DD/MM/YY DD/MM/YY\nПример: 22/10/22 30/10/22')


@bot.callback_query_handler(func=lambda call: call.data == "photo_yes")
def photos_yes(call: CallbackQuery) -> None:
    logger.info("Photos Yes callback")
    photos = True
    bot.send_message(call.from_user.id,
                     "Пожалуйста, отправьте количество фото вы хотите выгрузить.\nМаксимум 9 фотографий.")
    bot.set_state(call.from_user.id, UserData.photos_amount, call.from_user.id)
    with bot.retrieve_data(call.from_user.id, call.from_user.id) as data:
        data["photos"] = photos

@bot.callback_query_handler(func= lambda call: call.data == "photo_no")
def photos_no(call: CallbackQuery) -> None:
    logger.info("NO PHOTOS CALLBACK")
    photos = False
    bot.send_message(call.from_user.id,
                     "Отлично. Пожалуйста, отправьте любую цифру или число для продолжения")
    bot.set_state(call.from_user.id, UserData.api_response, call.from_user.id)
    ProcessData.save_data(user_id=call.from_user.id, dict_key="photos_amount", chat_id=call.from_user.id, data=photos)

@bot.callback_query_handler(func= lambda call: call.data.startswith("show_photo"))
def show_extra_photos(call: CallbackQuery) -> None:
    logger.info("SHOWING EXTRA PHOTOS")
    property_id = call.data.split("_")[2]
    with bot.retrieve_data(call.from_user.id, call.from_user.id) as data:
        photos_amount = data["photos_amount"]

    photos = HotelPhotos_methods.select_photo_links(hotel_id=property_id, photo_amount=photos_amount)
    bot.send_media_group(call.from_user.id, photos)





