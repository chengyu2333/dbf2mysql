# -*- coding: utf-8 -*
import time

# 数据路径
dbf_cache = "data/cache_%s.sqlite" % time.strftime("%Y%m%d")


# API配置
api_post = "http://120.55.59.164/stock/v1/rthq/"
api_id = "http://120.55.59.164/stock/v1/rthq/{id}/"
api_code = "http://120.55.59.164/stock/v1/rthq/?code={code}"

enable_thread = True  # 启用线程
thread_pool_size = 10  # 线程池大小
max_upload = 10  # 每次上传最大数据量

# 超时/出错重试次数
timeout_http = 100
retry_http = 1
# 重试等待时间（指数形式）
silence_http_multiplier = 2
silence_http_multiplier_max = 10

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