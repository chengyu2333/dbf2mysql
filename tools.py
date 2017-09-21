import hashlib
import os
import sys


def get_md5(file_path):
    md5 = None
    if os.path.isfile(file_path):
        f = open(file_path, 'rb')
        md5_obj = hashlib.md5()
        md5_obj.update(f.read())
        hash_code = md5_obj.hexdigest()
        f.close()
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