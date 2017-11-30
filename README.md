# DBF行情数据实时同步工具

## _待办_
"""
SQLAlchemy
!verify
twisted
python future
concurrent.futures


了解python开源社区
钻研精神
"""
get检查数据是否存在，不存在则标记status=0

## 背景
- 数据源每天生成一个文件夹
- 每隔12秒生成一个dbf格式的数据库文件
- 每个文件有1w多行记录
- 每次生成的文件只有一部分记录是有变动的

## 需求
- 每天有变动的数据实时同步到webservice，
- 数据库的字段可能与webservice的字段不同，需要有映射关系
- 同步之前可能还需要对数据的做相应的处理
- 保证数据的正确

## 变动数据对比算法
两个10000多条数据的文件对比其有变动的数据，并将变动的数据处理后上传到api服务器。
将数据读入到pandas，记录行数，并将做比对的数据也载入pandas，连接两个数据文件合并后去重，得到去重的结果后，剔除掉之前的数据，剩下的就是变动的数据。

## 同步策略
因为api服务器后台算法和性能问题，导致数据可能无法即时同步，需要修改同步策略。
即保证最新数据优先上传，有空余时间再采用类似“渐进式JPEG”算法对整体数据做平均补偿。
达到K线图先显示大体轮廓，再慢慢完善细节的效果。

## 程序功能
- 模式一：检测文件夹内的变动，对新增的数据文件分析，筛选出有变动的记录，映射处理后同步到webservice
- 模式二：检测某个数据文件是否有更新（本地或URL），缓存文件并同步上传

### config.py配置文件如下
```
# -*- coding: utf-8 -*
import time

# 数据文件的文件名或文件夹名
db_file_path = lambda :"/Data/LOneClient-2.3.2.25b/sanban/data/%s/nqhq/" % time.strftime("%Y%m%d")

# 数据文件列表缓存路径
db_list_cache = lambda: "tmp/list_cache_%s.txt" % time.strftime("%Y%m%d")
prev_file = "tmp/prev.dbf"

# 程序运行的时间段，格式%H%M%S, 为空时一直运行
# time_range = "093000-113000,133000-163000"
time_range_sync = ""

# API配置
api_post = "http://api.xxx.com/markets/v1/rthq/"
api_put = "http://api.xxx.com/markets/v1/rthq/{id}/"
api_get = "http://api.xxx.com/markets/v1/rthq/?code={code}"
post_json = False
post_success_code = 201

cycle_time = 7  # 程序最小扫描周期时间
upload_cycle = 20  # 文件最小上传周期时间
particle_size = 3  # 扫面粒度，跳过n-1个中间数据
reverse_list = True  # 倒序文件列表（即优先处理最新数据）

enable_thread = True  # 启用线程
thread_pool_size = 10  # 线程池大小

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
```
