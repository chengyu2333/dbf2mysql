# -*- coding: utf-8 -*
import io
import time
import os
import sys


class Log:
    def __init__(self, debug=True):
        self.print_log = debug
        if not os.path.exists("logs"):
            os.makedirs("logs")

    def log_error(self,msg):
        f = io.open("logs/" + time.strftime("%Y-%m-%d", time.localtime()) + " errors.log", 'a', encoding="utf-8")
        log = "\r\n" + time.ctime() + " | " + msg + "\r\n"
        if self.print_log:
            sys.stdout.write("\033[1;31m" + str(log) + "\033[0m")
        f.write(log)
        f.close()

    def log_success(self,msg):
        f = io.open("logs/" + time.strftime("%Y-%m-%d", time.localtime()) + " success.log", 'a', encoding="utf-8")
        log = "\r\n" + time.ctime() + " | " + msg + "\r\n"
        if self.print_log:
            sys.stdout.write("\033[1;33m" + str(log) + "\033[0m")
        f.write(log)
        f.close()


def view_bar(num, total):
    current = int(num/total*50)
    max_num = 50
    rate = num / total
    rate_num = rate * 100.0
    r = '\r[%s%s]%.2f%%  [%d/%d]' % ("="*current, " "*(max_num-current), rate_num, num, total)
    sys.stdout.write(r)
    sys.stdout.flush()