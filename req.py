# -*- coding: utf-8 -*
import requests
from urllib import request
import os
import io
import json
import collections
import threadpool
from retry import retry
import config
from log import Log
from tools import view_bar


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
        # print()
        if callback:callback(response)
        else:self.__callback(response)
        return response

    # get request
    def get_try(self, get_url, callback=None):
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


class PostReq(BaseReq):
    # batch post data to webservice
    def post_data(self, post_url, data_list, post_json=False, enable_thread=False,thread_pool_size=10,post_success_code=201):
        self.post_success_code = post_success_code
        self.data_total = len(data_list)
        if self.data_total:view_bar(0, self.data_total)
        else:return
        if not self.pool:
            self.pool = threadpool.ThreadPool(thread_pool_size)
        try:
            if enable_thread:
                args = []
                for data in data_list:
                    args.append(([post_url, data, post_json, self.__callback], None))
                reqs = threadpool.makeRequests(self.post_try, args)
                [self.pool.putRequest(req) for req in reqs]
                self.pool.wait()
                args.clear()
                reqs.clear()
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
            else:
                self.log.log_error("response error\ncode:%d\nresponse:%s\npost_data data:%s"
                              % (response.status_code,response,response))
        view_bar(self.processed_count, self.data_total)


class GetReq(BaseReq):
    # get last db file path
    @retry(stop_max_attempt_number=config.retry_http,
           wait_exponential_multiplier=config.silence_http_multiplier * 1000,
           wait_exponential_max=config.silence_http_multiplier_max * 1000)
    def get_db_file(self):
        if type(config.db_file_path) is not str:path = config.db_file_path()
        else:path = config.db_file_path

        if type(config.cache_dblist) is not str:cache_dblist = config.cache_dblist()
        else:cache_dblist = config.cache_dblist

        # get db file from local
        if config.local_source:
            if os.path.exists(path):
                # path is file
                if os.path.isfile(path):
                    time_temp_path = "tmp/old_time.tmp"
                    create_time = os.stat(path).st_ctime
                    if os.path.exists(time_temp_path):
                        f = open(time_temp_path, 'r+')
                        create_time_old = f.read()
                        create_time_old = float(create_time_old) if create_time_old else False
                    else:create_time_old = False
                    f = open(time_temp_path, 'w')
                    f.write(str(create_time))
                    f.close()
                    if not create_time_old or create_time_old < create_time:return path
                    else:return False
                #  if path is folder
                else:
                    try:
                        return self.pop_dbpath(path, cache_dblist)
                    except Exception as e:
                        self.log.log_error(str(e))
                        raise
        # get db file from url
        else:
            path = "tmp/dbf_cache_pool/cache.dbf"
            create_time_old = None
            if os.path.exists(path):
                create_time_old = os.stat(path).st_ctime
            request.urlretrieve(config.db_url, path)
            create_time = os.stat(path).st_ctime
            if not create_time_old or create_time_old < create_time:return path
            else:return False

    # update db file cache
    @staticmethod
    def update_dblist_cache(dblist_path, dbfile_path):
        try:
            dblist = os.listdir(dbfile_path)
            dblist.sort()
            dbdict = collections.OrderedDict()
            if os.path.exists(dblist_path):
                with open(dblist_path, 'r+', encoding="utf-8") as f:
                    lines = f.readlines()
                    for line in lines:
                        line = line.replace("\n", "")
                        line = line.split(" ")
                        dbdict[line[0]] = line[1]
                    for l in dblist:
                        if l not in dbdict:
                            dbdict[l] = "0"
                    f.seek(0)
                    f.truncate()
                    lines = ""
                    for l in dbdict:
                        lines += l + " " + dbdict[l] + "\n"
                    f.write(lines)
            else:
                lines = ""
                # if os.path.exists("tmp/prev.dbf"): os.remove("tmp/prev.dbf")
                for l in dblist:
                    lines += l + " " + "0\n"
                with open(dblist_path, 'w', encoding="utf-8") as f:
                    f.write(lines)
        except:
            raise

    # cache file list and pop File path
    def pop_dbpath(self, dbfile_path, cache_dblist, desc=False):
        dbdict = collections.OrderedDict()
        try:
            self.update_dblist_cache(cache_dblist, dbfile_path)
            with open(cache_dblist, 'r+', encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines:
                    line = line.replace("\n", "")
                    line = line.split(" ")
                    dbdict[line[0]] = line[1]
                if "0" in dbdict.values(): # if record have flag 0
                    dbpath = list(dbdict.keys())[list(dbdict.values()).index("0")]
                    dbdict[dbpath] = "1"
                    f.seek(0)
                    f.truncate()
                    lines = ""
                    for l in dbdict:
                        lines += l + " " + dbdict[l] + "\n"
                    f.write(lines)
                    return dbfile_path + dbpath
        except Exception as e:
            raise

    # 根据证券代码获取并缓存ID
    def get_id(self, code=833027):
        code = str(code)
        id_temp_path = "tmp/id_cache.txt"
        api_url = "http://api.chinaipo.com/markets/v1/rthq/?code=" + code
        id_list = {}
        # get id from cache
        if os.path.exists(id_temp_path):
            with open(id_temp_path, "r") as f:
                id_temp = f.read()
            if id_temp:
                id_list = json.loads(id_temp)
                if code in id_list:
                    return id_list[code]
        # get id from api
        response = requests.get(api_url)
        result = json.loads(response.text)
        if result['results']:
            result = result['results'][0]['id']
            id_list[code] = result
            with open(id_temp_path, "w") as f:
                f.write(json.dumps(id_list))
            return result
        else:
            return False


class Req(PostReq, GetReq):
    pass