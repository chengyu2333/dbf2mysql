import time


class Cron:
    def __init__(self, time_range=""):
        self.time_range = time_range

    def cycle_exec(self, func, arg, callback=None, cycle_time=10):
        while True:
            # 判断时间段
            if self.time_range:
                if not self.in_time_range(self.time_range):
                    time.sleep(cycle_time)
                    continue

            start_time = time.time()
            try:
                if callback:
                    if arg:
                        callback(func(arg))
                    else:
                        callback(func())
                else:
                    if arg:
                        func(arg)
                    else:
                        func()
            except Exception as e:
                raise

            # 保证固定周期时间
            end_time = time.time()
            sleep_time = cycle_time - (end_time - start_time)
            sleep_time = sleep_time if sleep_time >= 0 else 0
            time.sleep(sleep_time)

    def cycle(self, task=None):
        """
        :param task: task[(func,arg,callback,cycle),…]
        """
        start = time.time()
        while True:
            spend = int(time.time() - start)
            spend = 1 if spend < 1 else spend
            for a in task:
                if spend % a[3] == 0:
                    if a[2]:  # callback
                        if a[1]:  # arg
                            a[2](a[0](a[1]))
                        else:
                            a[2](a[0])
                    else:
                        if a[1]:
                            a[0](a[1])
                        else:
                            a[0]()
            time.sleep(1)

    # 当前时间是否在某个时00-间段
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

