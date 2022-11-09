import json
from re import search, findall
from typing import Dict
from requests import get, request, codes, Response
from database.model_functions.hotel_data import HotelData_Methods
from api_parse.api_utils import API_UTILS
from loader import logger
from states.process_data import ProcessData

class API:

    @staticmethod
    def request_to_api(url: str, headers: Dict, query_string: Dict) -> Response:
        """
        Обычный get запрос к апи, для возвращения locations_v3_json
        :params

        """
        try:
            location_json = get(url, params=query_string, headers=headers, timeout=10)
            if location_json.status_code == codes.ok:
                logger.info('GET REQUEST SUCESS')
                return location_json

        except Exception as e:
            logger.exception(e)

    @staticmethod
    def post_request(url: str, headers: Dict, payload: Dict) -> Response:

        try:
            location_json = request("POST", url, json=payload, headers=headers, timeout=10)

            if location_json.status_code == codes.ok:
                logger.info("POST REQUEST SUCESS")
                return location_json
        except Exception as e:
            logger.info(f"POST REQUEST UNSUCESSFUL, ERORR:\n{e}")

    @staticmethod
    def unpack_locationv3_json(json_str: str, city_group: str) -> Dict:
        logger.info("UNPACKING LOCATION_V3_JSON")
        city_data = {
            "fullName": [],
            "gaiaId": []
        }

        pattern = rf'(?<="{city_group}",).+?[\]]'

        find = search(pattern, json_str)
        if find:
            length = findall(r"regionNames", json_str)
            result = json.loads(f"{{{find[0]}}}")

            if length:
                for index, value in enumerate(length):
                    try:
                        regionNames = result["sr"][index]["regionNames"]["fullName"]
                        gaiaId = result["sr"][index]["gaiaId"]
                        city_data["gaiaId"].append(gaiaId)
                        city_data["fullName"].append(regionNames)

                    except Exception as e:
                        logger.info(f'UNPACKING LOCATION_V3_JSON FAILURE, ERROR: {e}')

                return city_data

    @staticmethod
    def unpack_propertiesv2_json(response: Response, city: str, photo_upload: bool, user_id: int,
                                 results_amount: int = 200, photos_amount: int = 3) -> str:
        hotels_found = list()
        logger.info("UNPACKING PROPERTIES_V2 JSON")
        utils = API_UTILS()

        payload = {
            "propertyId": ""
        }
        headers = utils.headers
        headers["content-type"] = "application/json"
        url = "https://hotels4.p.rapidapi.com/properties/v2/detail"
        find = ProcessData.check_validity_of_payload(search_param=city, response=response, chat_id=user_id)
        if find:
            result = response.json()
            properties = result["data"]["propertySearch"]["properties"]
            for current_property in range(results_amount):
                hotel_data = dict()
                try:

                    property_id = properties[current_property].get("id")
                    hotels_found.append(property_id)
                    hotel_exists = HotelData_Methods.check_if_hotel_exists(property_id=property_id)
                    if hotel_exists:
                        logger.info("HOTEL FOUND IN DATABASE")
                        hotel_data = HotelData_Methods.return_hotel_data(property_id=property_id)
                    else:
                        payload["propertyId"] = property_id
                        hotel_data["property_id"] = property_id
                        # hotel_data["hotel_url"] = f"https://www.hotels.com/ho{str(property_id)}/"
                        property_details_response = API.post_request(url=url, headers=headers, payload=payload)
                        if property_details_response:
                            property_details = ProcessData.process_property_details(response=property_details_response,
                                                                                    photo_upload=photo_upload,
                                                                                    photos_amount=photos_amount,
                                                                                    property_id=property_id)
                            hotel_data["address"] = property_details[0]
                        else:
                            hotel_data["address"] = "NOT FOUND"

                        hotel_name = properties[current_property].get("name")
                        distance_from_center = properties[current_property].get('destinationInfo').get(
                            "distanceFromMessaging")
                        hotel_data["hotel_name"] = hotel_name
                        hotel_data["distance_from_center"] = distance_from_center

                        price_display = properties[current_property].get("price").get("displayMessages")
                        if price_display:
                            nightly_price = price_display[0]["lineItems"][0]["price"].get("formatted")
                            total_price = price_display[1]["lineItems"][0].get("value")
                        else:
                            nightly_price, total_price = "NOT FOUND", "NOT FOUND"
                        reviews = properties[current_property]["reviews"]
                        reviews_score = reviews.get("score")
                        reviews_total = reviews.get("total")
                        hotel_data["nightly_price"] = nightly_price
                        hotel_data["total_price"] = total_price
                        hotel_data["reviews_score"] = reviews_score
                        hotel_data["reviews_total"] = reviews_total

                        if photo_upload:
                            photo_url = properties[current_property].get("propertyImage").get("image").get("url")
                            hotel_data["photo_url"] = photo_url
                    hotel_data["user_id"] = user_id

                    ProcessData.save_and_send_data(hotel_data=hotel_data, photo_upload=photo_upload, user_id=user_id,
                                                   hotel_exists=hotel_exists)

                except IndexError:
                    logger.info("INDEX ERRORS || NO HOTELS LEFT IGNORED")
                    break

                except Exception as e:
                    logger.exception(e)

        return ":".join(hotels_found)
