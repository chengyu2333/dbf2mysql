# -*- coding: utf-8 -*

import os
from retrying import retry
from simpledbf import Dbf5
from process.cache import Cache


class Get:
    @retry(stop_max_attempt_number=3)
    def read_dbf(self, path):
        if not os.path.exists(path):
            return None
        return Dbf5(path, codec="gbk").to_dataframe()

    def update_dblist_cache(self, db_list_cache, db_file_path):
        """更新数据文件列表缓存"""
        if not os.path.exists(db_file_path):
            return False
        cache = Cache(db_list_cache)
        try:
            dblist = os.listdir(db_file_path)
            # 存在缓存更新，不存在重新写入
            if os.path.exists(db_list_cache):
                cache.update_all(dblist, "0")
            else:
                cache.write_all(dblist, "0")
            return True
        except:
            raise

    # cache file list and pop File path
    def get_db_path(self, db_file_path, db_list_cache):
        cache = Cache(db_list_cache)
        try:
            # 更新数据
            if self.update_dblist_cache(db_list_cache, db_file_path):
                file_name, file_name_prev = cache.get_key("0")
                if file_name and file_name_prev:
                    cache.update(file_name, "1")
                    return db_file_path + file_name, db_file_path + file_name_prev
                if file_name:
                    # 如果只获取一个文件 ， 返回的两个路径都是它
                    cache.update(file_name, "1")
                    return db_file_path + file_name, db_file_path + file_name
            return "", ""
        except Exception as e:
            raise e
