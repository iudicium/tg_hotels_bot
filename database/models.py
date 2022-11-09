from peewee import *

db = SqliteDatabase("user.db")

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    user_id = IntegerField()
    user_name = CharField()
    date_of_command = DateTimeField()
    command = TextField()
    hotels_found = TextField()


class Hotel_Data(BaseModel):
    user_id = ForeignKeyField(User)
    property_id  = TextField(primary_key=True)
    hotel_name = TextField(unique=True)
    distance_from_center = TextField()
    nightly_price = TextField()
    total_price = TextField()
    address = TextField()
    photo_url = TextField(unique=True)
    reviews_score = IntegerField()
    reviews_total = IntegerField()




class Hotel_Photos(BaseModel):
    hotel_id = ForeignKeyField(Hotel_Data)
    photo_links = TextField(unique=True)








