# -*- coding: utf-8 -*

import io
import time
import os
import sys


class Log:
    def __init__(self, print_log=True):
        self.print_log = print_log
        if not os.path.exists("logs"):
            os.makedirs("logs")


    def log_error(self,msg):
        f = io.open("logs/" + time.strftime("%Y-%m-%d", time.localtime()) + " errors.log", 'a', encoding="utf-8")
        log = time.ctime() + " | \t" + msg + "\r\n\n"
        if self.print_log:
            sys.stdout.write("\033[1;31m" + str(log) + "\033[0m")
        f.write(log)
        f.close()


    def log_success(self,msg):
        f = io.open("logs/" + time.strftime("%Y-%m-%d", time.localtime()) + " success.log", 'a', encoding="utf-8")
        log = time.ctime() + " | \t" + msg + "\r\n\n"
        if self.print_log:
            sys.stdout.write("\033[1;33m" + str(log) + "\033[0m")
        f.write(log)
        f.close()