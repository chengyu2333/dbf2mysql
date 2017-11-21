# -*- coding: utf-8 -*
import json
import os

import requests
from simpledbf import Dbf5

import config
from retrying import retry
from process.cache import Cache


class GetReq:

    @retry(stop_max_attempt_number=3)
    def cache_id(self, code=833027):
        # TODO only remote
        """
        根据证券代码获取并缓存ID
        code: 证券代码
        only_remote: 不从本地获取
        """
        id_cache = "tmp/id_cache.txt"
        cache = Cache(id_cache)
        code = str(code)
        api_url = config.api_get.format(code=code)
        # get id from cache
        if os.path.exists(id_cache):
            id = cache.get_value(code)
            if id: return id[1]
        # get id from api
        response = requests.get(api_url)
        if response.status_code == 200:
            result = json.loads(response.text)
            if result['results']:
                result['results'].sort(key=lambda x: x['updated_at'])
                result = result['results'][-1]['id']
                cache.append(code, result)
                return result
            else:
                return False

    @staticmethod
    def get_sort_code():
        """获取排行榜的上股票代码并缓存"""
        api_list = config.api_stock_ranking
        sort_cache = Cache("tmp/sort_code.txt")
        for l in api_list:
            data = requests.get(l)
            data = json.loads(data.text)
            for d in data['results']:
                sort_cache.update(d['stock_code'], "1", True)


@retry(stop_max_attempt_number=3)
def read_dbf(path):
    if not os.path.exists(path):
        raise Exception("dbf file not exist")
    try:
        return Dbf5(path, codec="gbk").to_dataframe()
    except:
        raise