from database.models import User, db
from datetime import datetime
from loader import logger
from peewee import ModelSelect
class UserMethods:

    @staticmethod
    def create_record(user_id: int, user_name: str, date_of_command: datetime.now(), command: str, hotel_ids: str) -> None:
        logger.info("CREATING A RECORD FOR USER DATABASE")
        with db:
            User.create(user_id=user_id, user_name=user_name, date_of_command=date_of_command, command=command, hotels_found=hotel_ids)

    @staticmethod
    def check_if_user_exists(user_id: int) -> bool:
        logger.info("CHECKING IF USER EXISTS IN A DATABASE")
        user_id = User.select(User.user_id).where(User.user_id == user_id)
        for user in user_id:
            if user.user_id:
                return True
        return False

    @staticmethod
    def return_user_fields(user_id: int) -> ModelSelect:
        logger.info("RETURNING USER FIELDS")
        user_data = User.select().where(User.user_id == user_id)
        return user_data
    # @staticmethod
    # def return_hotel_and_user(user_id: int) -> peewee.ModelSelect:
    #     with db:
    #         user_data = User.select(User, Hotel_Data).join(Hotel_Data, on=(User.user_id == Hotel_Data.user_id)
    #                                                        ).where(
    #             (User.user_id == user_id) & (Hotel_Data.user_id == user_id))
    #         return user_data
