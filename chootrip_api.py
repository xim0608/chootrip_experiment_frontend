import os
import requests
from requests.exceptions import RequestException


class ChootripApi:
    BASE_URL = os.environ.get("BASE_URL")
    BASE_API_URL = BASE_URL + '/api/'

    @classmethod
    def get_prefectures(cls):
        return cls.request_api('prefectures/')

    @classmethod
    def get_cities(cls, prefecture_id):
        return cls.request_api("cities/?prefecture={}".format(int(prefecture_id)))

    @classmethod
    def get_city_spots(cls, city_id):
        return cls.request_api("spots/?city={}".format(int(city_id)))

    @classmethod
    def get_spot(cls, spot_id):
        spots = cls.request_api("spots/{}/".format(int(spot_id)))
        for spot in spots:
            if 'spotimage_set' in spot:
                if len(spot['spotimage_set']) > 0:
                    spot['image_url'] = spot['spotimage_set'][0]["url"]
        return spots

    @classmethod
    def get_city(cls, city_id):
        return cls.request_api("cities/{}/".format(int(city_id)))

    @classmethod
    def get_spots_by_title_search(cls, title_keyword):
        spots = cls.request_api("spots/?title__icontains={}".format(title_keyword))
        for spot in spots:
            spot['image_url'] = ''
            if len(spot['spotimage_set']) > 0:
                spot['image_url'] = spot['spotimage_set'][0]["url"]
        return spots

    @classmethod
    def request_api(cls, path):
        try:
            headers = {"content-type": "application/json"}
            result = requests.get(cls.BASE_API_URL + path, headers=headers)
            data = result.json()
            return data
        except RequestException:
            import traceback
            traceback.print_exc()
            return False
