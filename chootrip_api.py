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
    def get_cities(cls):
        return cls.request_api('cities/')

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
