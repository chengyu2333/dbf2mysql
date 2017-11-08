# -*- coding: utf-8 -*
import time

# 数据文件的文件名或文件夹名
#db_file_path = lambda :"/Data/LOneClient-2.3.2.25b/sanban/data/%s/nqhq/" % time.strftime("%Y%m%d")
db_file_path = "../dbf/"

# 数据文件列表缓存路径
db_list_cache = lambda: "tmp/list_cache_%s.txt" % time.strftime("%Y%m%d")
prev_file = "tmp/prev.dbf"

# 程序运行的时间段，格式%H%M%S, 为空时一直运行
# time_range = "093000-113000,133000-163000"
time_range_sync = ""

# API配置
api_post = "http://api.chinaipo.com/markets/v1/rthq/"
api_put = "http://api.chinaipo.com/markets/v1/rthq/{id}/"
api_get = "http://api.chinaipo.com/markets/v1/rthq/?code={code}"
post_json = False
post_success_code = 201

cycle_time = 7  # 程序扫描最小周期时间
upload_cycle = 20  # 文件上传周期时间
particle_size = 3  # 扫面粒度，1为全部，未扫描到的将跳过
reverse_list = True  # 倒序文件列表（即优先处理最新数据）

enable_thread = True  # 启用线程
thread_pool_size = 10  # 线程池大小

# 超时时间
timeout_http = 100

# 重试等待时间（指数形式）
silence_http_multiplier = 2
silence_http_multiplier_max = 10

# 超时/出错重试次数
retry_http = 1

print_log = True  # 输出日志到控制台

# 数据库字段和POST字段的映射关系
map_rule = {
    "strict": True,  # 严格模式将仅同步配置的map中的字段
    "lower": True,  # 将column转小写,只在非严格模式下有效
    "swap": True,  # 翻转key-value, 只能在严格模式开启
    "map": {
        # 格式 source_key:new_key
        "hqzqdm": "HQZQDM",
        "hqzqjc": "HQZQJC",
        "hqzrsp": "HQZRSP",
        "hqjrkp": "HQJRKP",
        "hqzjcj": "HQZJCJ",
        "hqcjsl": "HQCJSL",
        "hqcjje": "HQCJJE",
        "hqcjbs": "HQCJBS",
        "hqzgcj": "HQZGCJ",
        "hqzdcj": "HQZDCJ",
        "hqsyl1": "HQSYL1",
        "hqsyl2": "HQSYL2",
        "hqjsd1": "HQJSD1",
        "hqjsd2": "HQJSD2",
        "hqhycc": "HQHYCC",
        "hqssl5": "HQSSL5",
        "hqsjw5": "HQSJW5",
        "hqsjw4": "HQSJW4",
        "hqssl4": "HQSSL4",
        "hqsjw3": "HQSJW3",
        "hqssl3": "HQSSL3",
        "hqsjw2": "HQSJW2",
        "hqssl2": "HQSSL2",
        "hqsjw1": "HQSJW1",
        "hqssl1": "HQSSL1",
        "hqbjw1": "HQBJW1",
        "hqbsl1": "HQBSL1",
        "hqbjw2": "HQBJW2",
        "hqbsl2": "HQBSL2",
        "hqbjw3": "HQBJW3",
        "hqbsl3": "HQBSL3",
        "hqbjw4": "HQBJW4",
        "hqbsl4": "HQBSL4",
        "hqbjw5": "HQBJW5",
        "hqbsl5": "HQBSL5",
        "updated_at": "updated_at"
    }
}