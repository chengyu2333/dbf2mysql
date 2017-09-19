# -*- coding: utf-8 -*

local_source = True  # 是否使用本地数据源
db_url = "http://183.60.7.32/nqhq.dbf"
db_file_path = "nqhq/"  # 文件名或文件夹名
post_url = "http://api.chinaipo.com/markets/v1/rthq/"
# post_url = "http://127.0.0.1"
post_json = False
success_code = 201
# http://www.chinaipo.com/data/hangqing/833027/833027.php

cycle_time = 30  # 扫描周期
enable_thread = True  # 启用线程
thread_pool_size = 10  # 线程池大小
# cache_size = 100  # 数据库缓存大小

# 超时时间
timeout_http = 30
# timeout_db = 10

# 重试等待时间（指数形式）
# silence_db_multiplier = 2
# silence_db_multiplier_max = 10
silence_http_multiplier = 2
silence_http_multiplier_max = 10

# 超时/出错重试次数
retry_http = 5
retry_db = 5

print_log = True  # 输出日志到控制台

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