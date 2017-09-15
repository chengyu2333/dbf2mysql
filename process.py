import time
import config
import os
import log
from dbfread import DBF
from map_dict import map_dict
import req


def p_key(key):
    return key


def sync():
    if req.get_db_file(config.db_url, config.db_file):
        table = DBF(config.db_file, encoding="gbk", char_decode_errors="ignore")
        data = []
        updated_at = ""

        # read record as dict to list
        for record in table:
            if not updated_at:
                updated_at = str(record['HQZQJC'])+str(record['HQCJBS'])
                updated_at = time.strptime(updated_at,"%Y%m%d%H%M%S")
                print("updated as:",time.strftime("%Y-%m-%dT%H:%M:%S",updated_at))
                continue

            temp_row = {}
            temp_row['updated_at'] = time.strftime("%Y-%m-%dT%H:%M:%S",updated_at)
            for field in record:
                temp_row[field] = record[field]
            data.append(temp_row)
            # break

        new_data, total = map_dict(data,
                            config.map_rule['map'],
                            config.map_rule['strict'],
                            config.map_rule['lower'],
                            process_key=p_key,
                            exchange=config.map_rule['exchange'])
        log.log_success("total record: " + str(total))
        try:
            req.post_data_list(config.post_url, new_data)
        except Exception as e:
            print(str(e))
            raise




