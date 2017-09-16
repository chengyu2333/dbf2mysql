# -*- coding: utf-8 -*

import requests
from urllib import request
import os
import json
import threadpool
from retry import retry
import config
import log
<<<<<<< HEAD

=======
from database import DB

SUCCESS_COUNT = 0


# get db file,return is it newer
@retry(stop_max_attempt_number=config.retry_db,
       wait_exponential_multiplier=config.slience_db_multiplier * 1000,
       wait_exponential_max=config.slience_db_multiplier_max * 1000)
def get_db_file(db_url, db_file):

    return True

    ctime_old = None
    if os.path.exists(db_file):
        ctime_old = os.stat(db_file).st_ctime
    request.urlretrieve(db_url, db_file)
    ctime = os.stat(db_file).st_ctime

    if not ctime_old or ctime_old < ctime:
        return True
    else:
        return False

db = DB()


# batch post data to webservice
def post_data_list(url, data_list):
    is_json = config.post_json
    try:
        # for d in data_list:
        #     print(d)

        if config.enable_thread:  # multi thread
            args = []
            for d in data_list:
                args.append(([url, d, is_json], None))
            pool = threadpool.ThreadPool(config.thread_pool_size)
            reqs = threadpool.makeRequests(post_except, args, finished)
            [pool.putRequest(req) for req in reqs]
            pool.wait()
            args.clear()
        else:  # single thread
            #post_except(url, data_list)
            for d in data_list:
                # db.put_data(d)
                # continue
                res = post_except(url, d, is_json)
    except Exception:
        raise


# post callback
# def finished(*args):
#     global SUCCESS_COUNT
#     print("finished  ",args)
#     if args[1]:
#         print(args[1])
#         if args[1].status_code == 201:
#             SUCCESS_COUNT += 1
#         else:
#             log.log_error("post data failed\ncode:%d\nresponse:%s\npost_data:%s"
#                           % (args[1].status_code, args[1].text, args[0]))


# no exception handle, for implement retrying
@retry(stop_max_attempt_number=config.retry_http,
       wait_exponential_multiplier=config.slience_http_multiplier*1000,
       wait_exponential_max=config.slience_http_multiplier_max*1000)
def post_retry(url, data, is_json=False):
    try:
        if is_json:
            print("try…json… ", end="")
            j = json.dumps(data)
            print(type(j))
            return requests.post(url, json=json.dumps(data), timeout=config.timeout_http)
        else:
            print("try…str… ", end="")
            return requests.post(url, data=data, timeout=config.timeout_http)
    except Exception as e:
        print(str(e))
        raise


# have exception handle, for implement multi thread
def post_except(url, data, is_json=False):
    global SUCCESS_COUNT
    print("post_except:", url)
    try:
        res = post_retry(url, data, is_json)
        if res.status_code == 201:
            SUCCESS_COUNT += 1
        else:
            log.log_error("post data failed\ncode:%d\nresponse:%s\npost_data:%s"
                          % (res.status_code, res, data))
        return res
    except Exception as e:
        log.log_error("server error:" + str(e) + "\ndata:" + str(data))
        raise
>>>>>>> c66414c34bfd2453d165edfed66664394fdad100

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

    # try post data
    def post_try(self, post_url, data_list, post_json=False, callback=None):
        # print("post:", data_list, "  try ", end="")
        print((data_list))
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
        try:
            if enable_thread:
                args = []
                for data in data_list:
                    args.append(([post_url, data, post_json, self.__callback], None))
                print("args",len(args))
                pool = threadpool.ThreadPool(thread_pool_size)
                reqs = threadpool.makeRequests(self.post_try, args)
                [pool.putRequest(req) for req in reqs]
                pool.wait()
                args.clear()
            else:
                for d in data_list:
                    self.post_try(post_url, d, post_json, self.__callback)
        except Exception:
            raise

    def __callback(self, *args):
        self.processed_count += 1
        response = args[0]
        if response:

            if response.status_code == self.post_success_code:
                self.success_count += 1
                print("success")
            else:
                log.log_error("post data failed\ncode:%d\nresponse:%s\npost_data data:%s"
                              % (response.status_code,response,response))
        print(self.processed_count,"/",self.success_count)


class GetReq(BaseReq):
    # get db file, return is it newer
    @retry(stop_max_attempt_number=config.retry_db,
           wait_exponential_multiplier=config.silence_db_multiplier * 1000,
           wait_exponential_max=config.silence_db_multiplier_max * 1000)
    def get_db_file(self, db_url, db_file_path):
        return True # 测试本地文件

        create_time_old = None
        if os.path.exists(db_file_path):
            create_time_old = os.stat(db_file_path).st_ctime
        request.urlretrieve(db_url, db_file_path)
        create_time = os.stat(db_file_path).st_ctime

        if not create_time_old or create_time_old < create_time:return True
        else:return False

class Req(PostReq, GetReq):
    pass