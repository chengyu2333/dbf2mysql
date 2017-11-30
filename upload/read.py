# -*- coding: utf-8 -*
import os
import sqlite3
import pandas
from retrying import retry


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

    @retry(stop_max_attempt_number=3,
           wait_fixed=1000)
    def select_data(self, where, limit):
        path = self.path
        if not os.path.exists(path):
            raise Exception("file not exist")
        try:
            self.conn = sqlite3.connect(path)
            df = pandas.read_sql_query("SELECT * FROM %s WHERE %s ORDER BY updated_at ASC LIMIT %s" % (self.table, where, limit), con=self.conn)
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

# data = Read("data/cache_20171116.sqlite")
# print(data.select_data("status=0", "10"))
# data.last_update()
# print(data.exe_sql("select * from nqhq where status=0"))
