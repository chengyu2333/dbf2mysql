# -*- coding: utf-8 -*
from req_base import BaseReq
import config
import os
import json
import requests
from urllib import request
from retry import retry
from cache import Cache


class GetReq(BaseReq):

    @retry(stop_max_attempt_number=config.retry_http,
           wait_exponential_multiplier=config.silence_http_multiplier * 1000,
           wait_exponential_max=config.silence_http_multiplier_max * 1000)
    def get_db_file_from_url(self, url, path):
        """
        下载数据文件并返回路径
        """
        create_time_old = None
        if os.path.exists(path):
            create_time_old = os.stat(path).st_ctime
        request.urlretrieve(url, path)
        create_time = os.stat(path).st_ctime
        if not create_time_old or create_time_old < create_time:
            return path
        else:
            return False

    def get_db_file_from_file(self, path):
        """
        检测数据文件变动
        """
        time_temp_path = "tmp/old_time.tmp"
        create_time = os.stat(path).st_ctime
        if os.path.exists(time_temp_path):
            f = open(time_temp_path, 'r+')
            create_time_old = f.read()
            create_time_old = float(create_time_old) if create_time_old else False
        else:
            create_time_old = False
        f = open(time_temp_path, 'w')
        f.write(str(create_time))
        f.close()
        if not create_time_old or create_time_old < create_time:
            return path
        else:
            return False

    def update_dblist_cache(self, db_list_cache, db_file_path):
        """更新数据文件列表缓存"""
        cache = Cache(db_list_cache)
        try:
            dblist = os.listdir(db_file_path)
            # 倒序文件列表
            # dblist.sort()

            # 存在缓存更新，不存在重新写入
            if os.path.exists(db_list_cache):
                cache.update_all(dblist, "0")
            else:
                cache.write_all(dblist, "0")
        except:
            raise

    # cache file list and pop File path
    def get_db_file_from_folder(self, db_file_path, db_list_cache, desc=False):
        """
        从文件夹获取数据文件路径
        """
        cache = Cache(db_list_cache)
        try:
            file_name = ""
            self.update_dblist_cache(db_list_cache, db_file_path)
            for i in range(config.particle_size):
                file_name = cache.get_key("0")
            if file_name:
                cache.update(file_name, "1")
                return db_file_path + file_name
        except Exception as e:
            raise

    def get_db_file(self):
        """
        获取dbf数据文件路径 
        """
        # 检查配置
        if type(config.db_file_path) is not str:db_file_path = config.db_file_path()
        else:db_file_path = config.db_file_path

        if type(config.db_list_cache) is not str:db_list_cache = config.db_list_cache()
        else:db_list_cache = config.db_list_cache

        if "http://" in db_file_path or "https://" in db_file_path:
            # 从url获取
            return self.get_db_file_from_url(config.db_url, "tmp/dbf_cache_pool/cache.dbf")
        else:
            # 从本地获取
            if os.path.exists(db_file_path):
                if os.path.isfile(db_file_path):  # path is file
                    return self.get_db_file_from_file(db_file_path)
                else:  # if path is folder
                    return self.get_db_file_from_folder(db_file_path, db_list_cache)

    @retry(stop_max_attempt_number=3)
    def cache_id(self, code=833027, only_remote = False):
        # TODO only remote
        """
        根据证券代码获取并缓存ID
        code: 证券代码
        only_remote: 不从本地获取
        """
        id_cache = "tmp/id_cache.txt"
        cache = Cache(id_cache)
        code = str(code)
        api_url = config.api_get.format(code = code)
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
