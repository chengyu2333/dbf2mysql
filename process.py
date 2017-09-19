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
                  silence_http_multiplier=config.silence_http_multiplier,
                  silence_http_multiplier_max=config.silence_http_multiplier_max,
                  timeout_http=config.timeout_http)
        self.log = Log(print_log=config.print_log)
        self.data = []
        self.updated_at = ""
        self.skip = ['hqssl4', 'hqssl3', 'hqcjje', 'hqcjbs', 'hqbjw1', 'hqbjw5', 'hqzrsp', 'hqsjw3', 'hqzjcj', 'hqssl1', 'hqbsl2', 'hqbjw4', 'hqssl5', 'hqssl2', 'hqbsl5', 'hqcjsl', 'hqsjw4', 'hqhycc', 'hqsjw5', 'hqsyl1', 'hqzgcj', 'hqjsd2', 'hqbjw2', 'hqjsd1', 'hqbsl4', 'hqbsl1', 'hqsjw2', 'hqsyl2', 'hqbjw3', 'hqsjw1', 'hqjrkp', 'hqbsl3', 'hqzdcj']


    def sync(self):
        db_path = self.req.get_db_file()
        data = []
        updated_at = ""
        self.log.log_success("db_path:" + db_path)

        if db_path:
            try:
                table = DBF(db_path, encoding="gbk", char_decode_errors="ignore")
            except Exception as e:
                self.log.log_error(str(e))
                raise
            # get update time
            for record in table:
                if record['HQZQDM'] == "000000":
                    updated_at = str(record['HQZQJC']) + str(record['HQCJBS'])
                    updated_at = time.strptime(updated_at, "%Y%m%d%H%M%S")
                    updated_at = time.strftime("%Y-%m-%dT%H:%M:%S", updated_at)
                    break
            else:
                print("not found update_at field")

            # read record as dict append to list
            for record in table:
                temp_row = {'updated_at': updated_at}

                #  skip none value record
                skip = False
                for field in record:
                    temp_row[field] = record[field]
                    if field.lower() in self.skip and int(record[field]):
                        skip = True
                if skip:
                    continue
                else:
                    pass

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
                              post_success_code=config.success_code)

            except Exception as e:
                self.log.log_error(str(e))
                # raise
