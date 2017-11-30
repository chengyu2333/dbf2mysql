# -*- coding: utf-8 -*
import time

# 源数据路径
# db_file_path = "/Data/LOneClient-2.3.2.25b/sanban/data/%s/nqhq/" % time.strftime("%Y%m%d")
db_file_path = "../nqhq/"

# 文件列表缓存路径
dbf_list_cache = "tmp/list_cache_%s.txt" % time.strftime("%Y%m%d")
# 数据缓存路径
dbf_cache = "data/cache_%s.sqlite" % time.strftime("%Y%m%d")

api_stock_ranking = ["http://api.chinaipo.com/markets/v1/tchart/?baseIndex=all&sortBy=chng_pct&order=desc",
      "http://api.chinaipo.com/markets/v1/tchart/?baseIndex=all&sortBy=latest_quantity&order=desc",
      "http://api.chinaipo.com/markets/v1/tchart/?baseIndex=all&sortBy=latest_amount&order=desc",
      "http://api.chinaipo.com/markets/v1/tchart/?baseIndex=contract&sortBy=chng_pct&order=desc",
      "http://api.chinaipo.com/markets/v1/tchart/?baseIndex=contract&sortBy=latest_quantity&order=desc",
      "http://api.chinaipo.com/markets/v1/tchart/?baseIndex=contract&sortBy=latest_amount&order=desc"]

print_log = True  # 输出日志到控制台
