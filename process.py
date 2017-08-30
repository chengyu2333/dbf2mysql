import time
import config
import os
from dbfread import DBF
from map_dict import map_dict
import req


def p_key(key):
    return key


def sync():
    if req.get_db_file(config.db_url, config.db_file):
        table = DBF(config.db_file, char_decode_errors="ignore")
        data = []
        print("total: ",len(table))

        # for record in table:
        #     for field in record:
        #         print(field, " ", end="")
        #     print()
        #     break

        # read record as dict to list
        for record in table:
            temp_row = {}
            for field in record:
                temp_row[field] = record[field]
            data.append(temp_row)
            # break

        new_data, total = map_dict(data,
                            config.map_rule['map'],
                            config.map_rule['strict'],
                            config.map_rule['lower'],
                            process_key=p_key)
        print("total record: ",total)
        try:
            req.post_data(config.post_url, new_data)
        except Exception as e:
            print(str(e))
            raise




