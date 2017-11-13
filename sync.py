# -*- coding: utf-8 -*
import time
import shutil
import os
from simpledbf import Dbf5
from pandas import concat
import config
from log import Log
from dbfread import DBF
from map_dict import map_dict
from req import Req


class Sync:
    def __init__(self):
        self.req = Req(retry_http=config.retry_http,
                  silence_http_multiplier=config.silence_http_multiplier,
                  silence_http_multiplier_max=config.silence_http_multiplier_max,
                  timeout_http=config.timeout_http)
        self.log = Log(print_log=config.print_log)
        self.db_now = ""
        self.db_prev = ""
        self.table = None
        self.table_prev = None
        self.new_data = []

    def get(self, db_now=None, db_prev=None, get_all=False):
        """
        获取数据
        :return: DataFrame: (table，table_prev)
        """
        start_time = time.time()
        self.db_now = db_now or self.req.get_db_file()
        self.db_prev = db_prev or config.prev_file

        # 读文件表
        try:
            # db_now不存在
            if not self.db_now or not os.path.exists(self.db_now):
                if get_all:  # 取得全部数据
                    if self.db_prev or not os.path.exists(self.db_prev):
                        self.table = Dbf5(self.db_prev,codec="gbk").to_dataframe()
                    else:
                        print("file not exist")
                        return False
                else:
                    return False
            else:
                self.table = Dbf5(self.db_now, codec="gbk").to_dataframe()
                if os.path.exists(self.db_prev):
                    self.table_prev = Dbf5(self.db_prev, codec="gbk").to_dataframe()
            self.log.log_success("Read data spend:{time}s | prev dbf []: {db_prev} | now dbf []:{db_now}".
                                 format(time="%.2f" % (time.time()-start_time),
                                        db_prev=str(self.db_prev),
                                        db_now=str(self.db_now)))
            return self.table, self.table_prev
        except Exception as e:
            self.log.log_error(str(e))
            raise

    def process(self, table=None, table_prev=None):
        """
        处理、映射表数据
        :param table: 
        :param table_prev: 
        :return: new_data
        """
        start_time = time.time()
        # 原始数据
        table = table or self.table
        table_prev = table_prev or self.table_prev
        # 处理对比数据
        if not table_prev.empty:
            l = len(table_prev)
        else:
            l = 0
        dl = []
        df = concat([table_prev, table], ignore_index=True).drop_duplicates().ix[l:, :]

        # updated_at = str(df[df['HQZQDM']=="000000"]['HQZQJC']) + str(df[df['HQZQDM']=="000000"]['HQCJBS'])
        # 如果update_at不是今天，那么就设置为今天 (for data template)
        if str(df[df['HQZQDM']=="000000"]['HQZQJC']) == time.strftime("%Y%m%d"):
            updated_at = str(df[df['HQZQDM']=="000000"]['HQZQJC']) + str(df[df['HQZQDM']=="000000"]['HQCJBS'])
            updated_at = time.strptime(updated_at, "%Y%m%d%H%M%S")
            updated_at = time.strftime("%Y-%m-%dT%H:%M:%S", updated_at)
        else:
            updated_at = time.strftime("%Y-%m-%dT09:10:00")

        for row in df.iterrows():
            d = row[1].to_dict()
            d['updated_at'] = updated_at
            # 降低精度
            for r in d:
                if isinstance(d[r], float):
                    d[r] = "%.2f" % d[r]
            dl.append(d)

        # map dict
        new_data, total = map_dict(dl,
                                   config.map_rule['map'],
                                   config.map_rule['strict'],
                                   config.map_rule['lower'],
                                   swap=config.map_rule['swap'])
        # update db cache
        if self.db_now:
            shutil.copy(self.db_now, self.db_prev)

        self.new_data = new_data
        self.log.log_success("Process spend: {time}s | update at: {up_at} | new record: {new}"
                             .format(up_at=updated_at,  new=total,
                                     time="%.2f" % (time.time() - start_time)))
        return new_data

    def upload(self, data=None):
        """
        上传数据
        :param data: dict data
        :return: True or False
        """
        print("Start commit, total:", len(data))
        start_time = time.time()
        data = data or self.new_data
        # start commit all data
        try:
            self.req.commit_data_list(post_url=config.api_post,
                                      data_list=data,
                                      post_json=config.post_json,
                                      enable_thread=config.enable_thread,
                                      thread_pool_size=config.thread_pool_size,
                                      post_success_code=config.post_success_code)
        except Exception as e:
            self.log.log_error(str(e))
            return False
        self.new_data = None
        self.log.log_success("Commit finished,spend time:" + "%.2f" % (time.time() - start_time))
        return True

    def sync(self):
        self.get()
        self.process()
        self.upload()

    @staticmethod
    def reset():
        """重置缓存"""
        # 要删除的文件列表
        del_list = ["tmp/id_cache.txt", "tmp/old_time.tmp"]
        for d in del_list:
            if os.path.exists(d):
                os.remove(d)

    def cache_id_all(self):
        """缓存全部id"""
        table = DBF(config.prev_file, encoding="gbk", char_decode_errors="ignore")
        for record in table:
            try:
                print(record["HQZQDM"], "  ", self.req.cache_id(record["HQZQDM"]))
            except Exception as e:
                print(str(e))
