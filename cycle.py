import time


class Cron:
    def __init__(self, time_range, cycle_time):
        self.time_tange = time_range
        self.cycle_time = cycle_time

    def cycle_exec(self, func, cb=None):
        while True:
            # 判断时间段
            if self.time_range:
                if not self.in_time_range(self.time_range):
                    time.sleep(self.cycle_time)
                    continue

            start_time = time.time()
            try:
                func()
            except Exception as e:
                raise

            # 保证固定周期时间
            end_time = time.time()
            sleep_time = self.cycle_time - (end_time - start_time)
            sleep_time = sleep_time if sleep_time >= 0 else 0
            time.sleep(sleep_time)

    # 当前时间是否在某个时间段
    # 例如9:30-11:30,13:30-15:30
    # in_time_range("093000-113000,133000-153000")
    @staticmethod
    def in_time_range(ranges):
        now = time.strptime(time.strftime("%H%M%S"), "%H%M%S")
        ranges = ranges.split(",")
        for range in ranges:
            r = range.split("-")
            if time.strptime(r[0], "%H%M%S") <= now <= time.strptime(r[1], "%H%M%S") or time.strptime(r[0],"%H%M%S") >= now >= time.strptime(r[1], "%H%M%S"):
                return True
        return False


class executable:
    def __init__(self):
        pass

