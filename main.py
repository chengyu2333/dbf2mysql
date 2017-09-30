# -*- coding: utf-8 -*
import time
import config
from cache import Cache
from log import Log
from process import Process
log = Log(config.print_log)


cache_tpl = Cache("tmp/uploaded_tpl.txt")
process = Process()
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
def cycle_exec(cycle_time=10):
    re = False
    while True:
        # 判断时间段
        if config.time_range:
            if not in_time_range(config.time_range):
                time.sleep(cycle_time)
                continue
        start_time = time.time()
        try:
            # 检查当天是否已上传模
            if cache_tpl.get_value(time.strftime("%Y%m%d")):
                log.log_success("upload new template")
                process.sync(template=True)
            else:
                # 检查API是否正常
                error_count = process.check_random()
                print("miss count", error_count)
                if error_count > 4:
                    log.log_error("API error ，reupload template")
                    if process.sync(template=True):
                        continue

                if process.sync(template=False):
                    cache_tpl.put_item(time.strftime("%Y%m%d"), "1")

        except Exception as e:
            log.log_error(str(e))
            raise

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
    cycle_exec(cycle_time=config.cycle_time)