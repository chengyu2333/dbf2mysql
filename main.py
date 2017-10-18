# -*- coding: utf-8 -*
import time
import config
from cache import Cache
from log import Log
from sync import Sync
from req import GetReq as req_get
from cron import Cron
import os

log = Log(config.print_log)
cache_last_run = Cache("tmp/last_run.tmp")
cron = Cron(config.time_range)


# 当前时间是否在某个时间段
# 例如9:30-11:30,13:30-15:30
# in_time_range("093000-113000,133000-153000")
def in_time_range(ranges):
    now = time.strptime(time.strftime("%H%M%S"),"%H%M%S")
    ranges = ranges.split(",")
    for range in ranges:
        r = range.split("-")
        if time.strptime(r[0], "%H%M%S") <= now <= time.strptime(r[1], "%H%M%S") \
                or time.strptime(r[0], "%H%M%S") >= now >= time.strptime(r[1], "%H%M%S"):
            return True
    return False


# 周期执行函数
def cycle_exec(cycle_time=10):
    start_time = time.time()
    log = Log(print_log=config.print_log)
    datas = []

    while True:
        # 判断时间段
        if config.time_range:
            if not in_time_range(config.time_range):
                time.sleep(cycle_time)
                continue
        try:
            db_now = req_get().get_db_file()
            db_prev = config.prev_file
            sync = Sync()
            log.log_success("Start process, prev dbf: " + str(db_prev) + " now dbf:" + str(db_now))
            # 检查最后一次运行时间
            if not cache_last_run.get_value(time.strftime("%Y%m%d")):
                print("reset")
                sync.reset()
                cache_last_run.put_item(time.strftime("%Y%m%d"), "1")
                sync.sync()
                continue

            # 检查API是否正常
            # error_count = process.check_random()
            error_count = 0
            if error_count > 4:
                log.log_error("API error ，reupload template" + " miss count" + str(error_count))
                sync.reset()
                continue
            # 开始同步
            sync.get()
            datas += sync.process()
            print("len:", len(datas))
            if len(datas) > 9:
                sync.upload(datas)

        except Exception as e:
            log.log_error(str(e))
            raise

        # 保证固定周期时间
        end_time = time.time()
        sleep_time = cycle_time - (end_time - start_time)
        sleep_time = sleep_time if sleep_time>=0 else 0
        print('waiting…… %ds'%sleep_time)
        time.sleep(sleep_time)


if __name__ == "__main__":
    print("===== synchronize start =====")
    # sync = Sync()
    # task = [(sync.get, None, None, 5),
    #         (sync.process, None, None, 5),
    #         (sync.upload,None,None,30)]
    # cron.cycle(task)
    # process.reset()
    cycle_exec(cycle_time=config.cycle_time)
"""
流程:
loop:
    is first:
        rm id_cache prev.dbf
    sync(last.dbf, prev.dbf)
    cp last.dbf prev.dbf
"""
