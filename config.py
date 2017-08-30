db_url = "http://183.60.7.32/nqhq.dbf"
db_file = "nqhq.dbf"
post_url = "http://127.0.0.1:8080"

cycle_time = 12  # 扫描周期
enable_thread = False  # 启用线程
thread_pool_size = 1  # 线程池大小
cache_size = 1  # 缓存大小

# 超时时间
timeout_http = 1
timeout_db = 1

# 重试等待时间（指数形式）
slience_db_multiplier = 2
slience_db_multiplier_max = 10
slience_http_multiplier = 2
slience_http_multiplier_max = 10

# 超时/出错重试次数
retry_http = 5
retry_db = 5

print_log = True  # 输出日志到控制台

map_rule = {
    "strict": True,  # 严格模式将仅同步配置的map中的字段
    "lower": True,  # 将column转小写,只在非严格模式下有效
    "map": {
        # 格式 source_key:new_key
        "HQZQDM": "证券代码",
        "HQCJSL": "成交数量"
    }
}
