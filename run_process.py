import time
from read import Read
from lib.req_get import GetReq
from process import Process
from upload import Upload
from lib.log import Log
import config

r = Read()
p = Process()
u = Upload()
l = Log()
while True:
    path_now, path_last = GetReq().get_db_path(config.db_file_path, config.db_list_cache)
    if path_now or path_last:
        df_now = r.get_data(path_now)
        df_last = r.get_data(path_last)
    else:
        print(".", end="")
        time.sleep(1)

    data = p.process(df_last, df_now)
    print("path_now:", path_now, " path_last:", path_last, " new data:", len(data))
    if len(data) > 1:
        p.to_sql(data, "data/cache_%s.sqlite" % time.strftime("%Y%m%d"))

