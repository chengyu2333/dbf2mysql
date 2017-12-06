# -*- coding: utf-8 -*
import json
import time
import sqlite3
import requests
import threadpool
from retrying import retry

from .log import Log
from . import config

from .db import SessionManager
from . import model


class Commit:
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



    # POST一条数据
    @retry(stop_max_attempt_number=config.retry_http,
           wait_exponential_multiplier=config.silence_http_multiplier * 1000,
           wait_exponential_max=config.silence_http_multiplier_max * 1000)
    def post_data(self, data, cb=None):
        res = requests.post(config.api_post, data=data, timeout=self._timeout_http)
        if res.status_code == 201:
            # 验证服务器上是否有这条数据
            res_json = json.loads(res.text)
            id = res_json['id']
            res_id = requests.get(config.api_id.format(id=id))
            if res_id.status_code == 200:
                if cb: cb(True, data, res)
                return True
            else:
                if cb: cb(False, data, res)
                raise Exception("\npost成功，但服务器上没有这条数据")
        else:
            if cb: cb(False, data, res)
            raise Exception("\npost失败 " + str(res.status_code) + "\n" + str(data))


    # 批量提交数据
    def commit_data_list(self, post_url, data_list, enable_thread=False, thread_pool_size=10):
        self.data_total = len(data_list)
        if not self.pool:
            self.pool = threadpool.ThreadPool(thread_pool_size)
        try:
            if enable_thread:
                args = []
                for data in data_list:
                    args.append(([data, self.cb], None))
                reqs = threadpool.makeRequests(self.post_data, args)
                [self.pool.putRequest(req) for req in reqs]
                self.pool.wait()
                args.clear()
                reqs.clear()
            else:
                for d in data_list:
                    result = self.post_data(d)
                    if result:
                        self.success_count += 1
            count = self.success_count
            self.success_count = 0
            self.processed_count = 0
            return count
        except Exception:
            raise

    @staticmethod
    def verify_data(data, cb=None):
        res = requests.get(config.api_code.format(code=data['hqzqdm']))
        print(res.text)
        return res.status_code

    def verify_data_list(self, data_list):
        for d in data_list:
            result = self.verify_data(d)

    # 提交完毕的回调
    def cb(self, result, data=None, res=None):
        print(data)
        session = SessionManager().get_session()
        row = session.query(model.Nqhq).filter(model.Nqhq.HQZQDM==data['hqzqdm'], model.Nqhq.updated_at==data['updated_at']).one()
        if result:
            row.status = 1
        else:
            row.status = -1
        session.commit()
