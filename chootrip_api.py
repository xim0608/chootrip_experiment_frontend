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
        return cls.request_api("spots/{}/".format(int(spot_id)))

    @classmethod
    def get_spots(cls, spot_ids):
        spot_ids = list(map(lambda spot_id: str(spot_id), spot_ids))
        return cls.request_api("spots/?id__in={}".format(','.join(spot_ids)))

    @classmethod
    def get_city(cls, city_id):
        return cls.request_api("cities/{}/".format(int(city_id)))

    @classmethod
    def get_spots_by_title_search(cls, title_keyword):
        return cls.request_api("spots/?title__icontains={}".format(title_keyword))

    @classmethod
    def get_topics(cls):
        return cls.request_api("topics/")

    @classmethod
    def get_recommend(cls, spot_ids):
        import json
        print('get recommend')
        try:
            headers = {"content-type": "application/json"}
            data = {'spot_ids': spot_ids}
            result = requests.get(cls.BASE_API_URL + 'recommend/', data=json.dumps(data), headers=headers)
            data = result.json()
            return data
        except RequestException:
            import traceback
            traceback.print_exc()
            return False

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
