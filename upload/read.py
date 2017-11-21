# -*- coding: utf-8 -*
import os
import sqlite3

import pandas
from simpledbf import Dbf5

from retrying import retry
from process.cache import Cache


class Read:
    def __init__(self, path=""):
        self.code = "gbk"
        self.path = path
        self.last_id = pandas.Series
        self.conn = None
        self.table = "nqhq"

    def __del__(self):
        if self.conn:
            self.conn.close()

    @retry(stop_max_attempt_number=3)
    def _read_dbf(self, path):
        if not os.path.exists(path):
            raise Exception("dbf file not exist")
        try:
            return Dbf5(path, codec=self.code).to_dataframe()
        except:
            raise

    @retry(stop_max_attempt_number=3,
           wait_fixed=1000)
    def _read_sqlite(self, path):
        try:
            self.conn = sqlite3.connect(path)
            df = pandas.read_sql_query("SELECT * FROM %s" % self.table, con=self.conn)
        except:
            raise
        return df

    def get_data(self, path=""):
        path = self.path or path
        if path:
            if "dbf" in path:
                return self._read_dbf(path)
            elif "sqlite" in path:
                return self._read_sqlite(path)

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
                    cache.update(file_name, "1")
                    return db_file_path + file_name, None
            return None, None
        except Exception as e:
            raise e

    @retry(stop_max_attempt_number=3,
           wait_fixed=1000)
    def select_data(self, where, limit):
        path = self.path
        if not os.path.exists(path):
            raise Exception("file not exist")
        try:
            self.conn = sqlite3.connect(path)
            df = pandas.read_sql_query("SELECT * FROM %s WHERE %s LIMIT %s" % (self.table, where, limit), con=self.conn)
            self.last_id = df['HQZQDM']
            return df
        except:
            raise

    @retry(stop_max_attempt_number=3,
           wait_fixed=1000)
    def exe_sql(self, sql):
        path = self.path
        if not path:
            raise Exception("file not exist")
        try:
            conn = sqlite3.connect(path)
            df = pandas.read_sql_query(sql, con=conn)
            return df
        except:
            raise

data = Read("data/cache_20171116.sqlite")
# print(data.select_data("status=0", "10"))
# data.last_update()
# print(data.exe_sql("select * from nqhq where status=0"))
