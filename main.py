import time
import config
import process


# 时间是否在时间段中
def in_times(time,time_interval):
    # 判断时间区间
    h = int(time.strftime("%H"))
    m = int(time.strftime("%M"))
    print(h," ",m)
    if h>=9 and h<=11 or h>=13 and h<=15:
        if h==9 and m>=10:
            pass
        else:
            return
    else:
        return False

# 周期执行某函数
def cycle_exec(func, cycle_time=10):
    while True:
        start_time = time.time()

        func()

        # 保证固定周期时间
        end_time = time.time()
        sleep_time = config.cycle_time - (end_time - start_time)
        sleep_time = sleep_time if sleep_time>=0 else 0
        print("process finised,spend time:", end_time - start_time)
        print('waiting…… %ds'%sleep_time)
        time.sleep(sleep_time)


def run():
    while True:
        start_time = time.time()
        process.sync()
        # 保证固定周期时间
        end_time = time.time()
        sleep_time = config.cycle_time - (end_time - start_time)
        sleep_time = sleep_time if sleep_time>=0 else 0
        print("process finised,spend time:", end_time - start_time)
        print('waiting…… %ds'%sleep_time)
        time.sleep(sleep_time)

# run()

cycle_exec(process.sync, config.cycle_time)