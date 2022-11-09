from config_data.config import  RAPID_API_KEY, API_HOST
class API_UTILS:
    def __init__(self) -> None:

        self.location_url = "https://hotels4.p.rapidapi.com/locations/v3/search"
        self.headers =  {
            "X-RapidAPI-Key": RAPID_API_KEY,
            "X-RapidAPI-Host": API_HOST
        }
        self.properties_url = "https://hotels4.p.rapidapi.com/properties/v2/list"

#