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
        self.data = []
        self.updated_at = ""

    def sync(self):
        db_path = self.req.get_db_file()
        data = []
        data_cache = {}
        updated_at = ""
        dbf_cache = "tmp/cache.dbf"
        self.log.log_success("start process, db path: " + str(db_path))

        if db_path:
            try:
                if os.path.isfile(db_path):
                    # print("new db:", get_md5(db_path))
                    table = DBF(db_path, encoding="gbk", char_decode_errors="ignore")
                # the last dbf file
                if os.path.isfile(dbf_cache):
                    # print("last db:", get_md5(dbf_cache))
                    table_cache = DBF(dbf_cache, encoding="gbk", char_decode_errors="ignore")
                else: table_cache = []

            except Exception as e:
                self.log.log_error(str(e))
                raise
            # convert table_cache to list
            for record in table_cache:
                data_cache[record['HQZQDM']] = record
            # get update time
            for record in table:
                if record['HQZQDM'] == "000000":
                    updated_at = str(record['HQZQJC']) + str(record['HQCJBS'])
                    updated_at = time.strptime(updated_at, "%Y%m%d%H%M%S")
                    updated_at = time.strftime("%Y-%m-%dT%H:%M:%S", updated_at)
                    break

            # read record as dict append to list
            skip_count = 0
            for record in table: # iteration every row
                temp_row = {}
                skip = False
                if data_cache and str(record) == str(data_cache[record['HQZQDM']]):
                    skip = True
                    skip_count += 1
                else:
                    for field in record:  # iteration every field
                        temp_row[field] = record[field]
                    temp_row['updated_at'] = updated_at
                    data.append(temp_row)
            # update db cache
            shutil.copy(db_path, dbf_cache)
            # map key
            new_data, total = map_dict(data,
                                       config.map_rule['map'],
                                       config.map_rule['strict'],
                                       config.map_rule['lower'],
                                       swap=config.map_rule['swap'])
            self.log.log_success("update at: {updated_at}, total record: {total}, new record: {new}"
                                 .format(updated_at=updated_at, total=total+skip_count, new=total))
            # start post all data
            try:
                self.req.post_data(post_url=config.api_post,
                                   data_list=new_data,
                                   post_json=config.post_json,
                                   enable_thread=config.enable_thread,
                                   thread_pool_size=config.thread_pool_size,
                                   post_success_code=config.post_success_code)

            except Exception as e:
                self.log.log_error(str(e))
                # raise

    def cache_id(self):
        table = DBF("tmp/nqhq.dbf", encoding="gbk", char_decode_errors="ignore")
        for record in table:
            try:
                print(record["HQZQDM"], "  ", self.req.get_id(record["HQZQDM"]))
            except Exception as e:
                print(str(e))

