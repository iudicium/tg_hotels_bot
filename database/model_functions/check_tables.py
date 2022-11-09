from database.models import User, Hotel_Data, Hotel_Photos, db
from loader import logger
def check_if_tables_exist() -> None:
    with db:
        tables = [User, Hotel_Data, Hotel_Photos]
        if not all(table.table_exists() for table in tables):
            logger.info("TABLES DO NOT EXIST || CREATING TABLES")
            db.create_tables(tables)
        else:
            logger.info("TABLES EXIST ALREADY || NOT CREATING TABLES")