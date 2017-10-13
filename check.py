import os
from req import Req
from cache import Cache

def check_random():
    """
    检查API服务器是否正常
    随机抽取10个数据是否存在，否则重新上传一遍
    第一次运行结束后检查cache/total是否小于11000， 否则重新上传
    """
    import random
    path = "tmp/prev.dbf"
    if not os.path.exists(path):
        return 0
    table = DBF(path, encoding="gbk", char_decode_errors="ignore")
    success = 0
    failed = 0
    for record in table:
        if random.random() < 0.8:
            continue
        if success + failed > 10:
            break
        try:
            re = self.req.cache_id(record["HQZQDM"])
        except Exception as e:
            print(str(e))
        if re:
            success += 1
            # print("ok")
        else:
            failed += 1
            # print("failed")
    return failed

def check_total():
    cache_id = Cache("tmp/id_cache").read_cache()
    print(len(cache_id))

check_total()