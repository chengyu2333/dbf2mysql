import time

from .log import Log
from . import config
from .get import Get
from .process import Process

g = Get()
p = Process()
l = Log()


def once(path_now=None, path_last=None):
    t = time.time()
    try:
        if not path_now and not path_last:
            path_now, path_last = g.get_db_path(config.db_file_path, config.dbf_list_cache)
        if path_now and path_last:
            # 有新数据
            df_now = g.read_dbf(path_now)
            df_last = g.read_dbf(path_last)
            if path_now == path_last:
                # 上传全部
                # data = p.process(None, df_last)
                # 过滤第一个文件
                data = p.first(df_last)
            else:
                data = p.process(df_last, df_now)
            print(time.strftime("%Y-%m-%d %H:%M:%S"),
                  ' current:…', path_now[-20:],
                  " last:…", path_last[-20:],
                  " data:", len(data),
                  " spend:", "%.2fs" % (time.time()-t))
            if len(data) > 0:
                p.to_sql(data, config.dbf_cache)
        else:
            time.sleep(1)
    except Exception as e:

        raise
        l.log_error(str(e))


def run():
    print("===== Start process =====")
    while True:
        once()

