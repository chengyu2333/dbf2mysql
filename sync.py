# -*- coding: utf-8 -*
import time
import shutil
import os
import config
from log import Log
from dbfread import DBF
from map_dict import map_dict
from req import Req
from tools import get_md5


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

    def get(self):
        """
        获取数据文件
        :return: table，table_prev
        """
        self.db_now = self.req.get_db_file()
        self.db_prev = config.prev_file
        # db_now文件是否存在
        # if not self.db_now or not os.path.exists(self.db_now):
        #     return False

        # 读文件表
        try:
            # db_now不存在
            if not self.db_now or not os.path.exists(self.db_now):
                # db_prev不存在
                if not self.db_prev or not os.path.exists(self.db_prev):
                    print("no file need sync")
                    return False
                else:
                    self.table = DBF(self.db_prev, encoding="gbk", char_decode_errors="ignore")
            else:
                self.table = DBF(self.db_now, encoding="gbk", char_decode_errors="ignore")
                if os.path.exists(self.db_prev):
                    self.table_prev = DBF(self.db_prev, encoding="gbk", char_decode_errors="ignore")
            self.log.log_success("Start process, prev dbf: " + str(self.db_prev) + " now dbf:" + str(self.db_now))
        except Exception as e:
            self.log.log_error(str(e))
            raise
        return self.table, self.table_prev

    def process(self, table=None, table_prev=None):
        """
        处理、映射表数据
        :param table: 
        :param table_prev: 
        :return: new_data
        """
        start_time = time.time()
        skip_count = 0
        # 原始表数据
        table = table or self.table
        table_prev = table_prev or self.table_prev
        # 处理后的数据
        data = []
        data_prev = {}

        # convert table_prev to dict
        if table_prev:
            for record in table_prev:
                data_prev[record['HQZQDM']] = record

        # get update_at
        for record in table:
            if record['HQZQDM'] == "000000":
                # 如果update_at不是今天，那么就设置为今天 (for data template)
                if str(record['HQZQJC']) == time.strftime("%Y%m%d"):
                    updated_at = str(record['HQZQJC']) + str(record['HQCJBS'])
                    updated_at = time.strptime(updated_at, "%Y%m%d%H%M%S")
                    updated_at = time.strftime("%Y-%m-%dT%H:%M:%S", updated_at)
                else:
                    updated_at = time.strftime("%Y-%m-%dT%H:%M:%S")
                break

        # read record as dict append to list
        for record in table:  # iteration each row
            temp_row = {}
            if record['HQZQDM'] in data_prev and str(record) == str(data_prev[record['HQZQDM']]):
                skip_count += 1
            else:
                for field in record:  # iteration every field
                    # 降低float精度
                    if isinstance(record[field], float):
                        record[field] = "%.2f" % record[field]
                    temp_row[field] = record[field]
                temp_row['updated_at'] = updated_at
                data.append(temp_row)

        # map dict
        new_data, total = map_dict(data,
                                   config.map_rule['map'],
                                   config.map_rule['strict'],
                                   config.map_rule['lower'],
                                   swap=config.map_rule['swap'])
        # update db cache
        if self.db_now:
            shutil.copy(self.db_now, self.db_prev)

        self.new_data = new_data
        self.log.log_success("Process spend: {time} update at: {up_at}, total record: {total}, new record: {new}"
                             .format(up_at=updated_at, total=total + skip_count, new=total,
                                     time=time.time() - start_time))
        return new_data

    def upload(self, data=None):
        """
        上传数据
        :param data: dict data
        :return: True or False
        """
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
        self.log.log_success("Commit finished,spend time:" + str(time.time() - start_time))
        return True

    def sync(self):
        self.get()
        self.process()
        self.upload()

    def reset(self):
        """重置一天的同步"""
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