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
        db_now = self.req.get_db_file()
        db_prev = config.prev_file  # Last processed file
        # if not db_now and os.path.exists(db_prev):
        #     print("上传最后一个缓存")
        #     db_now = db_prev
        #     db_prev = ""
        data = []
        data_cache = {}
        updated_at = ""
        if db_now:
            start_time = time.time()
            self.log.log_success("start process, prev dbf: " + str(db_prev) + " not dbf:" + str(db_now))
            # read dbf file
            try:
                if os.path.exists(db_now):
                    # print("new db:", get_md5(db_path))
                    table = DBF(db_now, encoding="gbk", char_decode_errors="ignore")
                # the last dbf file
                if os.path.exists(db_prev):
                    # print("last db:", get_md5(dbf_prev))
                    table_cache = DBF(db_prev, encoding="gbk", char_decode_errors="ignore")
                else: table_cache = []
            except Exception as e:
                self.log.log_error(str(e))
                raise

            # convert table_cache to dict
            for record in table_cache:
                data_cache[record['HQZQDM']] = record

            print("Convert table_cache to dict:", time.time()-start_time)

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
                if record['HQZQDM'] in data_cache and str(record) == str(data_cache[record['HQZQDM']]):
                    skip_count += 1
                else:
                    for field in record:  # iteration every field
                        temp_row[field] = record[field]
                    temp_row['updated_at'] = updated_at
                    # print(temp_row)
                    # print(data_cache[record['HQZQDM']])
                    data.append(temp_row)

            print("Analysis of change and combination of data:", time.time() - start_time)

            # update db cache
            shutil.copy(db_now, db_prev)

            print("copy previous file:", time.time()-start_time)
            # if db_prev:
            #     shutil.copy(db_now, db_prev)
            # else:
            #     os.remove(config.prev_file)
            # map key
            new_data, total = map_dict(data,
                                       config.map_rule['map'],
                                       config.map_rule['strict'],
                                       config.map_rule['lower'],
                                       swap=config.map_rule['swap'])

            print("map data:", time.time() - start_time)

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

            print("upload data:", time.time() - start_time)

            return True


    def cache_id(self):
        table = DBF("tmp/nqhq.dbf", encoding="gbk", char_decode_errors="ignore")
        for record in table:
            try:
                print(record["HQZQDM"], "  ", self.req.get_id(record["HQZQDM"]))
            except Exception as e:
                print(str(e))
