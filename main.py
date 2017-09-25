# -*- coding: utf-8 -*
import time
import config
from log import Log
from process import Sync
log = Log(config.print_log)


# 当前时间是否在某个时间段
# 例如9:30-11:30,13:30-15:30
# in_time_range("093000-113000,133000-153000")
def in_time_range(ranges):
    now = time.strptime(time.strftime("%H%M%S"),"%H%M%S")
    ranges = ranges.split(",")
    for range in ranges:
        r = range.split("-")
        if time.strptime(r[0],"%H%M%S") <= now <= time.strptime(r[1],"%H%M%S") or time.strptime(r[0],"%H%M%S") >= now >=time.strptime(r[1],"%H%M%S"):
            return True
    return False


# 周期执行函数
def cycle_exec(func, cycle_time=10):
    while True:
        # 判断时间段
        if config.time_range:
            if not in_time_range(config.time_range):
                time.sleep(cycle_time)
                continue

        start_time = time.time()
        try:
            re = func()
        except Exception as e:
            log.log_error(str(e))

        # 保证固定周期时间
        end_time = time.time()
        sleep_time = cycle_time - (end_time - start_time)
        sleep_time = sleep_time if sleep_time>=0 else 0
        if re:
            log.log_success("process finished,spend time:" + str(end_time - start_time))
            print('waiting…… %ds'%sleep_time)
        time.sleep(sleep_time)
        # time.sleep(1)  # 多睡眠1s，方便查看log

if __name__ == "__main__":
    print("synchronize start")
    cycle_exec(Sync().sync, config.cycle_time)
    # TODO 优化对比算法，优化线程