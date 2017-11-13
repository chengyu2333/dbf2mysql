import hashlib
import os
import sys
import time

def get_md5(file_path):
    md5 = None
    if os.path.isfile(file_path):
        with open(file_path, 'rb') as f:
            md5_obj = hashlib.md5()
            md5_obj.update(f.read())
        hash_code = md5_obj.hexdigest()
        md5 = str(hash_code).lower()
    return md5


def view_bar(num, total):
    current = int(num/total*50)
    max_num = 50
    rate = num / total
    rate_num = rate * 100.0
    r = '\r[%s%s]%.2f%%  [%d/%d]' % ("="*current, " "*(max_num-current), rate_num, num, total)
    sys.stdout.write(r)
    sys.stdout.flush()


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