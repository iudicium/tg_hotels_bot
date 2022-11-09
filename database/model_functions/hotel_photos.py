from loader import logger
from typing import List, Union, Dict
from database.models import Hotel_Photos, db
from telebot.types import  InputMediaPhoto
class HotelPhotos_methods:
    @staticmethod
    def select_photo_links(hotel_id: str, photo_amount: int) -> List[InputMediaPhoto]:
        photos = []
        logger.info("SELECTING PHOTO LINKS FROM DATABASE")
        with db:
            photo_links = Hotel_Photos.select(Hotel_Photos.photo_links).where(Hotel_Photos.hotel_id == hotel_id)
            for index, photo in enumerate(photo_links):
                photos.append(InputMediaPhoto(photo.photo_links))
                if photo_amount == index:
                    return photos



    @staticmethod
    def process_extra_photos(response_json: Dict, property_id: str) -> List[str]:
        photos = list()
        for photo in range(50):
            try:
                images = response_json["propertyGallery"]["images"][photo]["image"]["url"]
                if images:
                    with db:
                        db_photos = Hotel_Photos.create(hotel_id=property_id, photo_links=images)
                        db_photos.save()
                photos.append(images)
            except IndexError:
                logger.info("PROCESSING PROPERTY DETAILS NO MORE PHOTOS LEFT")
                break
        return photos

