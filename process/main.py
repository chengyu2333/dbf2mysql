import time

from .log import Log
from . import config
from .get import Get
from .process import Process

g = Get()
p = Process()
l = Log()


def once(path_now=None, path_last=None):
    try:
        if not path_now and not path_last:
            path_now, path_last = g.get_db_path(config.db_file_path, config.dbf_list_cache)
        if path_now and path_last:
            # 有新数据
            df_now = g.read_dbf(path_now)
            df_last = g.read_dbf(path_last)
            if path_now == path_last:
                data = p.first(df_last)
            else:
                data = p.process(df_last, df_now)
            print('path_now:', path_now, " path_last:", path_last, " new data:", len(data))
            if len(data) > 0:
                p.to_sql(data, config.dbf_cache)
        else:
            time.sleep(1)
    except Exception as e:
        l.log_error(str(e))


def run():
    print("===== Start process =====")
    while True:
        once()

