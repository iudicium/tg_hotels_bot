from typing import Union, Tuple
from loader import bot
from typing import Any, List, Dict
from datetime import datetime
from pprint import pprint
from requests import Response
from re import search, Match
from loader import logger
from keyboards.inline.inline_button import Inline
from database.model_functions.hotel_data import  HotelData_Methods
from database.model_functions.hotel_photos import  HotelPhotos_methods

class ProcessData:
    @staticmethod
    def save_data(user_id: int, chat_id: int, dict_key: str, data: Any) -> None:
        """"
        DICT_KEY: Ключ в классе UserData()
        data: Any любая дата которую хотим сохранить.
        Функция существует просто для того что бы было более красиво сохранять данные
        """
        with bot.retrieve_data(user_id, chat_id) as user_data:
            user_data[dict_key] = data

    @staticmethod
    def create_rooms_object(adults: str, children_ages: List[int]) -> List:
        rooms_object = [{"adults": int(adults), "children": []}]
        for index, value in enumerate(children_ages):
            rooms_object[0]["children"].append({"age": int(value)})
        return rooms_object

    @staticmethod
    def print_data(user_id: int, chat_id: int) -> None:
        with bot.retrieve_data(user_id, chat_id) as data:
            pprint(data)

    @staticmethod
    def check_validity_of_payload(search_param: str, response: Response, chat_id: int) -> Union[Match[str], None]:
        try:
            find = search(search_param, response.text)

            if find and find is not None:
                return find
            raise Exception
        except Exception:
            logger.info("AN ERROR HAPPENED IN THE VALIDITY OF PAYLOAD")
            logger.info(response.text)
            bot.send_message(chat_id=chat_id,
                             text="Ваши параметры не нашли результатов. || Эта ошибка может возникать из-за проблем с сервером тоже.\nМожете вводить команду опять")
            bot.set_state(chat_id, None, chat_id)
            return None

    @staticmethod
    def finalize_payload(data: Any, sort: str, result_size: int) -> Dict:

        dates = data["date"]
        date_in, date_out = dates[0], dates[1]
        payload = {
            "destination": {"regionId": data["city"]},
            "checkInDate": {
                "day": date_in.day,
                "month": date_in.month,
                "year": date_in.year
            },
            "checkOutDate": {
                "day": date_out.day,
                "month": date_out.month,
                "year": date_out.year
            },
            "rooms": data["adults_children"],
            "resultsStartingIndex": 0,
            "resultsSize": result_size,
            "sort": sort,
            "filters": data["price"]
        }

        return payload

    @staticmethod
    def save_and_send_data(hotel_data: Dict, photo_upload: bool, user_id: int, hotel_exists: bool) -> None:
        property_id, address, hotel_name, distance_from_center, nightly_price, total_price, review_score, review_total, photo_url, uid = hotel_data.values()

        logger.info("SAVING AND SENDING DATA")
        if distance_from_center is None:
            distance_from_center = "RIGHT AT THE CENTER"
            hotel_data["distance_from_center"] = distance_from_center
        if not hotel_exists:
            HotelData_Methods.save_hotel_data(hotel_data=hotel_data)
        if photo_upload:
            markup = Inline.add_buttons(text=["Показать Фото"], callback=[f"show_photo_{hotel_data['property_id']}"])
            msg = f"""
                HOTEL NAME: {hotel_name} 🌍
DISTANCE FROM CENTER: {distance_from_center} ✅
NIGHTLY PRICE: {nightly_price}
TOTAL PRICE: {total_price} 🤑
REVIEW SCORE: {review_score} 🎖️
TOTAL REVIEWS: {review_total}!
ADRESS: {address}



                  """
            bot.send_photo(chat_id=user_id, photo=hotel_data["photo_url"], caption=msg, reply_markup=markup)
        else:
            msg = f"""
                 HOTEL NAME: {hotel_name} 🌍
DISTANCE FROM CENTER: {distance_from_center} ✅
NIGHTLY PRICE: {nightly_price}
TOTAL PRICE: {total_price} 🤑
REVIEW SCORE: {review_score} 🎖️
TOTAL REVIEWS: {review_total}!
ADRESS: {address}

            """
            bot.send_message(user_id, msg)
        #

    @staticmethod
    def check_single_date(date: str) -> datetime.strptime:

        try:
            check_date = datetime.strptime(date, "%d/%m/%y")

            return check_date
        except ValueError:
            return None

    @staticmethod
    def check_dates_validity(dates: List[str]) -> Union[None, Tuple]:
        if len(dates) != 2:
            return None
        else:
            date_in = ProcessData.check_single_date(date=dates[0])
            date_out = ProcessData.check_single_date(date=dates[1])
            if date_out is None or date_in is None:
                return None
            return date_in, date_out


    @staticmethod
    def process_property_details(property_id: str, response: Response, photo_upload: bool, photos_amount: int = 3) -> Tuple:
        pattern = rf'(?<="{property_id}",).+?[\]]'
        try:
            find = search(pattern, response.text)
            if find:
                response_json = response.json()["data"]["propertyInfo"]
                address = response_json["summary"]["location"]["address"].get("addressLine")
                hotel_check = HotelData_Methods.check_if_hotel_exists(property_id=property_id)
                if hotel_check:
                    photo_links = HotelPhotos_methods.select_photo_links(hotel_id=property_id, photo_amount=photos_amount)
                    return address, photo_links
                else:
                    if photo_upload:
                        photos = HotelPhotos_methods.process_extra_photos(response_json=response_json, property_id=property_id)
                        return address, photos
        except Exception as e:
            logger.info("Cannot retrieve adress and extra photos. Returning Not Found for adress and ")
            logger.exception(e)
            address = "Not found"
            photos = []
            return address, photos


