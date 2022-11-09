from typing import Dict
from database.models import Hotel_Data, db
from loader import logger
class HotelData_Methods:
    # TODO ADD MORE METHODS IF NEEDED
    @staticmethod
    def return_hotel_data(property_id: str) -> Dict:
        logger.info("RETURNING HOTEL DATA")
        hotel_dict = dict()
        with db:
            hotel_data = Hotel_Data.select().where(property_id == Hotel_Data.property_id)
        for hotel in hotel_data:
            hotel_dict["property_id"] = hotel.property_id
            hotel_dict["address"] = hotel.address
            hotel_dict["hotel_name"] = hotel.hotel_name
            hotel_dict["distance_from_center"] = hotel.distance_from_center
            hotel_dict["nightly_price"] = hotel.nightly_price
            hotel_dict["total_price"] = hotel.total_price
            hotel_dict["reviews_score"] = hotel.reviews_score
            hotel_dict["reviews_total"] = hotel.reviews_score
            hotel_dict["photo_url"] = hotel.photo_url
        return hotel_dict

    @staticmethod
    def check_if_hotel_exists(property_id: str) -> bool:
        logger.info("CHECKING IF HOTEL EXISTS IN DATABASE")
        hotel_data = Hotel_Data.select(Hotel_Data.property_id)
        for index, value in enumerate(hotel_data):

            if value.property_id == property_id:
                return True
        return False

    @staticmethod
    def save_hotel_data(hotel_data: Dict) -> None:
        with db:
            Hotel_Data.insert_many([hotel_data]).execute()
        logger.info("HOTEL EXISTS || NOT SAVING INTO DATABASE")
