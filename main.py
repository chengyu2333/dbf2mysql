# -*- coding: utf-8 -*
import time
import config
from log import Log
from process import Sync
log = Log(config.print_log)


# 当前时间是否在某个时间段
# 例如9:30-11:30,13:30-15:30
# in_time_range("093000-113000","133000-153000")
def in_time_range(*args):
    now = time.strftime("%H%M%S")
    for arg in args:
        if len(arg) == 13:
            range = arg.split("-")
            if range[0] <= now <= range[1] or range[0] >= now >=range[1]:
                print(True)
                return True
        else:
            raise Exception("时间格式不正确，如093000-113000")
    return False
# in_time_range("093000-113000","133000-183000")


# 周期执行函数
def cycle_exec(func, cycle_time=10):
    while True:
        start_time = time.time()
        try:
            func()
        except Exception as e:
            log.log_error(str(e))

        # 保证固定周期时间
        end_time = time.time()
        sleep_time = cycle_time - (end_time - start_time)
        sleep_time = sleep_time if sleep_time>=0 else 0
        log.log_success("process finished,spend time:" + str(end_time - start_time))
        print('waiting…… %ds'%sleep_time)
        time.sleep(sleep_time)
        time.sleep(1)  # 多睡眠1s，方便查看log

if __name__ == "__main__":
    cycle_exec(Sync().sync, config.cycle_time)