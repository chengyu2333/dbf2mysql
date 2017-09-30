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

    def sync(self, template=False):
        db_now = self.req.get_db_file()
        db_prev = config.prev_file  # Last processed file
        if template:
            print("上传最后一个缓存")
            db_now = db_prev
            db_prev = ""
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
                        if isinstance(record[field],float):
                            record[field] = "%.2f" % record[field]

                        temp_row[field] = record[field]
                    temp_row['updated_at'] = updated_at
                    data.append(temp_row)

            print("Analysis of change and combination of data:", time.time() - start_time)

            # update db cache
            if not template:
                shutil.copy(db_now, db_prev)

            print("copy previous file:", time.time()-start_time)

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
                self.req.commit_data_list(post_url=config.api_post,
                                          data_list=new_data,
                                          post_json=config.post_json,
                                          enable_thread=config.enable_thread,
                                          thread_pool_size=config.thread_pool_size,
                                          post_success_code=config.post_success_code)
            except Exception as e:
                self.log.log_error(str(e))
            return True

    def cache_id_all(self):
        table = DBF("tmp/prev.dbf", encoding="gbk", char_decode_errors="ignore")
        for record in table:
            try:
                print(record["HQZQDM"], "  ", self.req.cache_id(record["HQZQDM"]))
            except Exception as e:
                print(str(e))

    def check_random(self):
        import random
        # 随机抽取10个数据是否存在，否则重新上传一遍
        # 检查total是否小于11000， 否则重新上传
        path = "tmp/prev.dbf"
        if not os.path.exists(path):
            return 0
        table = DBF(path, encoding="gbk", char_decode_errors="ignore")
        success = 0
        failed = 0
        for record in table:
            if random.random()<0.8:
                continue
            if success + failed > 10:
                break
            try:
                re = self.req.cache_id(record["HQZQDM"])
            except Exception as e:
                print(str(e))
            if re:
                success += 1
                # print("ok")
            else:
                failed += 1
                # print("failed")
        return failed

# print(Process().check_random())
# Process().cache_id_all()
# Process().sync(False)
