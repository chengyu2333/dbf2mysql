# -*- coding: utf-8 -*
import time

# 数据文件的文件名或文件夹名
# db_file_path = "/Data/LOneClient-2.3.2.25b/sanban/data/%s/nqhq/" % time.strftime("%Y%m%d")
db_file_path = "../dbf/"

# 数据文件列表缓存路径
dbf_list_cache = "tmp/list_cache_%s.txt" % time.strftime("%Y%m%d")
dbf_cache = "data/cache_%s.sqlite" % time.strftime("%Y%m%d")


# 程序运行的时间段，格式%H%M%S, 为空时一直运行
# time_range = "093000-113000,133000-163000"
time_range_sync = ""

# API配置
# api_host = "http://api.chinaipo.com"
# api_host = "http://120.55.59.164"
api_host = "baidu.com"
api_post = api_host + "/markets/v1/rthq/"
api_put = api_host + "/markets/v1/rthq/{id}/"
api_get = api_host + "/markets/v1/rthq/?code={code}"

api_stock_ranking = ["http://api.chinaipo.com/markets/v1/tchart/?baseIndex=all&sortBy=chng_pct&order=desc",
      "http://api.chinaipo.com/markets/v1/tchart/?baseIndex=all&sortBy=latest_quantity&order=desc",
      "http://api.chinaipo.com/markets/v1/tchart/?baseIndex=all&sortBy=latest_amount&order=desc",
      "http://api.chinaipo.com/markets/v1/tchart/?baseIndex=contract&sortBy=chng_pct&order=desc",
      "http://api.chinaipo.com/markets/v1/tchart/?baseIndex=contract&sortBy=latest_quantity&order=desc",
      "http://api.chinaipo.com/markets/v1/tchart/?baseIndex=contract&sortBy=latest_amount&order=desc"]

post_json = False
post_success_code = 201

cycle_time = 2  # 程序最小扫描周期时间
upload_cycle = 20  # 文件最小上传周期时间
particle_size = 3  # 扫面粒度，跳过n-1个中间数据
# reverse_list = False  # 倒序文件列表（即优先处理最新数据）

enable_thread = True  # 启用线程
thread_pool_size = 10  # 线程池大小
max_upload = 100  # 每次上传的最大数据量

# 超时时间
timeout_http = 100
# 上传延迟
sleep = 0.1

# 重试等待时间（指数形式）
silence_http_multiplier = 2
silence_http_multiplier_max = 10

# 超时/出错重试次数
retry_http = 1

print_log = True  # 输出日志到控制台

# 数据库字段和POST字段的映射关系
map_rule = {
    "strict": False,  # 严格模式将仅同步配置的map中的字段
    "lower": True,  # 将column转小写,只在非严格模式下有效
    "swap": False,  # 翻转key-value, 只能在严格模式开启
    "map": {
    }
}