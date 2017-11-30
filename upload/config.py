# -*- coding: utf-8 -*
import time

# 数据路径
dbf_cache = "data/cache_%s.sqlite" % time.strftime("%Y%m%d")


# API配置
api_post = "http://120.55.59.164/stock/v1/rthq/"
api_id = "http://120.55.59.164/stock/v1/rthq/{id}/"
api_code = "http://120.55.59.164/markets/v1/rthq/?code={code}"

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
    "strict": False,  # 严格模式将仅同步配置的map中的字段
    "lower": True,  # 将column转小写,只在非严格模式下有效
    "swap": False,  # 翻转key-value, 只能在严格模式开启
    "map": {
    }
}