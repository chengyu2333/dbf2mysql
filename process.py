# -*- coding: utf-8 -*

import time
import config
from log import Log
from dbfread import DBF
from map_dict import map_dict
from req import Req


class Sync:
    def __init__(self):

        self.req = Req(retry_http=config.retry_http,
                  silence_http_multiplier=config.silence_db_multiplier,
                  silence_http_multiplier_max=config.silence_http_multiplier_max,
                  timeout_http=config.timeout_http)
        self.log = Log(print_log=config.print_log)
        self.data = []
        self.updated_at = ""


    def sync(self):
        if self.req.get_db_file(config.db_url, config.db_file_path):
            table = DBF(config.db_file_path, encoding="gbk", char_decode_errors="ignore")
            data = []
            updated_at = ""
            # get update time
            for record in table:
                if record['HQZQDM'] == "000000":
                    updated_at = str(record['HQZQJC']) + str(record['HQCJBS'])
                    updated_at = time.strptime(updated_at, "%Y%m%d%H%M%S")
                    updated_at = time.strftime("%Y-%m-%dT%H:%M:%S", updated_at)

            # read record as dict append to list
            for record in table:
                temp_row = {'updated_at': updated_at}
                for field in record:
                    temp_row[field] = record[field]
                data.append(temp_row)
            # map key
            new_data, total = map_dict(data,
                                       config.map_rule['map'],
                                       config.map_rule['strict'],
                                       config.map_rule['lower'],
                                       swap=config.map_rule['swap'])
            self.log.log_success("total record: %s update at: %s" % (str(total),updated_at))
            # start post all data
            try:
                self.req.post_data(post_url=config.post_url,
                              data_list=new_data,
                              post_json=config.post_json,
                              enable_thread=config.enable_thread,
                              thread_pool_size=config.thread_pool_size,
                              post_success_code=201)
            except Exception as e:
                print(str(e))
                raise
