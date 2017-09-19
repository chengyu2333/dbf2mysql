# -*- coding: utf-8 -*
import configparser
import requests
from urllib import request
import os
import io
import json
import threadpool
from retry import retry
import config
from log import Log


class BaseReq:
    def __init__(self,
                 retry_http=3,
                 silence_http_multiplier=2,
                 silence_http_multiplier_max=60,
                 timeout_http=10):
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
        # print("post:", data_list, "  try ", end="")
        # print(data_list)
        @retry(stop_max_attempt_number=self._retry_http,
               wait_exponential_multiplier=self._silence_http_multiplier * 1000,
               wait_exponential_max=self._silence_http_multiplier_max * 1000)
        def __post_retry():
            # print(".", end="")
            try:
                if post_json:
                    return requests.post(post_url, json=json.dumps(data_list), timeout=self._timeout_http)
                else:
                    return requests.post(post_url, data=data_list, timeout=self._timeout_http)
            except Exception as e:
                print(str(e))
                raise
        response = __post_retry()
        # print()
        if callback:callback(response)
        else:self.__callback(response)
        return response

    # get request
    def get_try(self, get_url, callback=None):
        # print("get:", get_url, "try ", end="")
        @retry(stop_max_attempt_number=self._retry_http,
               wait_exponential_multiplier=self._silence_http_multiplier * 1000,
               wait_exponential_max=self._silence_http_multiplier_max * 1000)
        def get_retry_inner():
            # print(".", end="")
            try:
                return requests.get(get_url)
            except Exception as e:
                print(str(e))
                raise
        response = get_retry_inner()
        # print()
        if callback:callback(response)
        else:self.__callback(response)
        return response

    # request callback
    def __callback(self, *args):
        print(args)


class PostReq(BaseReq):
    # batch post data to webservice
    def post_data(self, post_url, data_list, post_json=False, enable_thread=False,thread_pool_size=10,post_success_code=201):
        self.post_success_code = post_success_code
        if not self.pool:
            self.pool = threadpool.ThreadPool(thread_pool_size)
        try:
            if enable_thread:
                args = []
                for data in data_list:
                    args.append(([post_url, data, post_json, self.__callback], None))
                print("record count:", len(args))
                # pool = threadpool.ThreadPool(thread_pool_size)
                reqs = threadpool.makeRequests(self.post_try, args)
                [self.pool.putRequest(req) for req in reqs]
                self.pool.wait()
                args.clear()
                reqs.clear()
                pool = None
            else:
                for d in data_list:
                    self.post_try(post_url, d, post_json, self.__callback)
            self.success_count = 0
            self.processed_count = 0

        except Exception:
            raise

    def __callback(self, *args):
        self.processed_count += 1
        response = args[0]
        if response:

            if response.status_code == self.post_success_code:
                self.success_count += 1
                # print("success")
            else:
                self.log.log_error("post data failed\ncode:%d\nresponse:%s\npost_data data:%s"
                              % (response.status_code,response,response))
        print(self.processed_count,"/",self.success_count)


class GetReq(BaseReq):
    # get last db file path
    @retry(stop_max_attempt_number=config.retry_http,
           wait_exponential_multiplier=config.silence_http_multiplier * 1000,
           wait_exponential_max=config.silence_http_multiplier_max * 1000)
    def get_db_file(self):
        if config.local_source:
            try:
                return self.pop_dbpath(config.db_file_path)
            except Exception as e:
                self.log.log_error(str(e))
                raise
        else:
            path = "tmp/temp.dbf"
            create_time_old = None
            if os.path.exists(path):
                create_time_old = os.stat(path).st_ctime
            request.urlretrieve(config.db_url, path)
            create_time = os.stat(path).st_ctime
            if not create_time_old or create_time_old < create_time:return path
            else:return False

    @staticmethod
    def create_dblist(dblist_path, dbfile_path):
        f = io.open(dblist_path, 'a+', encoding="utf-8")
        list = os.listdir(dbfile_path)
        json.dump(list, f)
        f.close()

    def pop_dbpath(self, dbfile_path):
        dblist_path = "tmp/dblist.txt"
        if not os.path.isfile(dblist_path):
            self.create_dblist(dblist_path, dbfile_path)
        f = io.open(dblist_path, 'r', encoding="utf-8")
        list = json.load(f)
        dbpath = list.pop()
        f.close()
        f = io.open(dblist_path, 'w', encoding="utf-8")
        json.dump(list,f)
        f.close()
        return dbfile_path + dbpath


class Req(PostReq, GetReq):
    pass