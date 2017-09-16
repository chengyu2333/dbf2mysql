# -*- coding: utf-8 -*

from pymongo import MongoClient

class DB:
    __db = None
    __table = None

    def __init__(self):
        client = MongoClient("127.0.0.1", 12345)
        self.__db = client["nqhq"]

    def get_mongodb_conn(self, table_name):
        return self.__db[table_name]

    def put_data(self, data):
        try:
            self.__db["nqhq"].insert(data)
        except Exception:
            raise
