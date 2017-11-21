import time

import config
from lib.log import Log
from process.process import Process
from process.get import Get
from upload.read import Read


def run():
    g = Get()
    r = Read()
    p = Process()
    l = Log()
    while True:
        try:
            path_now, path_last = r.get_db_path(config.db_file_path, config.dbf_list_cache)
            if path_now or path_last:
                df_now = g.read_dbf(path_now)
                df_last = g.read_dbf(path_last)
                data = p.process(df_last, df_now)
                print('path_now:', path_now, " path_last:", path_last, " new data:", len(data))
                if len(data) > 1:
                    p.to_sql(data, config.dbf_cache)
            else:
                time.sleep(1)
        except Exception as e:
            l.log_error(str(e))
