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


class Process:
    def __init__(self):
        self.req = Req(retry_http=config.retry_http,
                  silence_http_multiplier=config.silence_http_multiplier,
                  silence_http_multiplier_max=config.silence_http_multiplier_max,
                  timeout_http=config.timeout_http)
        self.log = Log(print_log=config.print_log)
        self.data = []
        self.updated_at = ""

    def sync(self, db_now, db_prev=""):
        """
        同步一个dbf文件
        :param db_now: 待同步的dbf文件路径
        :param db_prev: 用于变动对比的dbf文件路径
        :return: 成功与否
        """
        start_time = time.time()
        # db_now = self.req.get_db_file()
        # db_prev = config.prev_file  # Last processed file
        if not db_now or not os.path.exists(db_now):
            return False

        data = []
        data_prev = {}
        table_prev = None
        updated_at = ""
        skip_count = 0

        # read dbf file
        try:
            # print("new db:", get_md5(db_now))
            table = DBF(db_now, encoding="gbk", char_decode_errors="ignore")
            if os.path.exists(db_prev):
                # print("last db:", get_md5(db_prev))
                table_prev = DBF(db_prev, encoding="gbk", char_decode_errors="ignore")
        except Exception as e:
            self.log.log_error(str(e))
            raise
        # convert table_prev to dict
        if table_prev:
            for record in table_prev:
                data_prev[record['HQZQDM']] = record

        self.log.log_success("Start synchronize, prev dbf: " + str(db_prev) + " now dbf:" + str(db_now))

        # get update_at
        for record in table:
            if record['HQZQDM'] == "000000":
                updated_at = str(record['HQZQJC']) + str(record['HQCJBS'])
                updated_at = time.strptime(updated_at, "%Y%m%d%H%M%S")
                updated_at = time.strftime("%Y-%m-%dT%H:%M:%S", updated_at)
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
        # update db cache
        shutil.copy(db_now, db_prev)
        # map dict
        new_data, total = map_dict(data,
                                   config.map_rule['map'],
                                   config.map_rule['strict'],
                                   config.map_rule['lower'],
                                   swap=config.map_rule['swap'])
        self.log.log_success("Process spend: {time} update at: {up_at}, total record: {total}, new record: {new}"
                             .format(up_at=updated_at, total=total + skip_count, new=total, time=time.time() - start_time))
        # start commit all data
        try:
            self.req.commit_data_list(post_url=config.api_post,
                                      data_list=new_data,
                                      post_json=config.post_json,
                                      enable_thread=config.enable_thread,
                                      thread_pool_size=config.thread_pool_size,
                                      post_success_code=config.post_success_code)
        except Exception as e:
            self.log.log_error(str(e))
        self.log.log_success("Commit finished,spend time:" + str(time.time() - start_time))
        return True

    def reset(self):
        """重置一天的同步"""
        del_list = ["tmp/id_cache.txt", config.prev_file, "tmp/old_time.tmp"]
        for d in del_list:
            if os.path.exists(d):
                os.remove(d)

    def cache_id_all(self):
        """缓存全部id"""
        table = DBF("tmp/prev.dbf", encoding="gbk", char_decode_errors="ignore")
        for record in table:
            try:
                print(record["HQZQDM"], "  ", self.req.cache_id(record["HQZQDM"]))
            except Exception as e:
                print(str(e))

# print(Process().check_random())
# Process().cache_id_all()
# Process().sync(False)
