import time
from read import Read
from lib.req_get import GetReq
from process import Process
from upload import Upload
import config

r = Read()
p = Process()
u = Upload()


# path_now, path_last = GetReq().get_db_path(config.db_file_path, config.db_list_cache)
path_now = "./tmp/first.dbf"
path_last = "./tmp/last.dbf"
print(path_now)
print(path_last)

df_now = r.get_data(path_now)
df_last = r.get_data(path_last)

data = p.process(df_last, df_now)
p.to_sql(data, "tmp/cache.sqlite")

print(len(data))

# u.upload(data)


# dfdata = p.drop_duplicate(df_last, df_now)
# dfdata = p.convert(dfdata)
# dfdata = p.filter(dfdata)
#
# print(dfdata)
#
# dictdata = p.to_dict(dfdata)
# print(len(dictdata))

# data = p.map(dictdata)
# print(len(data))

