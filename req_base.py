# -*- coding: utf-8 -*
import requests
import json
from retry import retry
import config
from log import Log


class BaseReq:
    def __init__(self,
                 retry_http=3,
                 silence_http_multiplier=2,
                 silence_http_multiplier_max=60,
                 timeout_http=10):
        self.data_total = 0
        self.processed_count = 0
        self.success_count = 0
        self.post_success_code = 201
        self._retry_http = retry_http
        self._silence_http_multiplier = silence_http_multiplier
        self._silence_http_multiplier_max = silence_http_multiplier_max
        self._timeout_http = timeout_http
        self.log = Log(True)
        self.pool = None

    # try post data
    def post_try(self, post_url, data_list, post_json=False, callback=None):
        @retry(stop_max_attempt_number=self._retry_http,
               wait_exponential_multiplier=self._silence_http_multiplier * 1000,
               wait_exponential_max=self._silence_http_multiplier_max * 1000)
        def __post_retry():
            try:
                if post_json:
                    return requests.post(post_url, json=json.dumps(data_list), timeout=self._timeout_http)
                else:
                    return requests.post(post_url, data=data_list, timeout=self._timeout_http)
            except Exception as e:
                print(str(e))
                raise
        response = __post_retry()
        if callback:callback(response)
        else:self.__callback(response)
        return response

    # get request
    def get_try(self, get_url, callback=None):
        @retry(stop_max_attempt_number=self._retry_http,
               wait_exponential_multiplier=self._silence_http_multiplier * 1000,
               wait_exponential_max=self._silence_http_multiplier_max * 1000)
        def get_retry_inner():
            try:

                return requests.get(get_url)
            except Exception as e:
                print(str(e))
                raise
        response = get_retry_inner()
        if callback:callback(response)
        else:self.__callback(response)
        return response

    def put_data(self,id ,data, callback=None):
        @retry(stop_max_attempt_number=config.retry_http,
               wait_exponential_multiplier=config.silence_http_multiplier * 1000,
               wait_exponential_max=config.silence_http_multiplier_max * 1000)
        def put_date_inner():
            api_put = "http://api.chinaipo.com/markets/v1/rthq/{id}/".format(id=id)
            try:
                return requests.put(api_put,data)
            except Exception as e:
                print(str(e))
                raise
        response = put_date_inner()
        if callback:callback(response)
        else:self.__callback(response)
        return response

    # request callback
    def __callback(self, *args):
        print(args)

