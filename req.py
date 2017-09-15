import requests
from urllib import request
import os
import json
import threadpool
from retry import retry
import config
import log
from database import DB

SUCCESS_COUNT = 0


# get db file,return is it newer
@retry(stop_max_attempt_number=config.retry_db,
       wait_exponential_multiplier=config.slience_db_multiplier * 1000,
       wait_exponential_max=config.slience_db_multiplier_max * 1000)
def get_db_file(db_url, db_file):

    return True

    ctime_old = None
    if os.path.exists(db_file):
        ctime_old = os.stat(db_file).st_ctime
    request.urlretrieve(db_url, db_file)
    ctime = os.stat(db_file).st_ctime

    if not ctime_old or ctime_old < ctime:
        return True
    else:
        return False

db = DB()


# batch post data to webservice
def post_data_list(url, data_list):
    is_json = config.post_json
    try:
        # for d in data_list:
        #     print(d)

        if config.enable_thread:  # multi thread
            args = []
            for d in data_list:
                args.append(([url, d, is_json], None))
            pool = threadpool.ThreadPool(config.thread_pool_size)
            reqs = threadpool.makeRequests(post_except, args, finished)
            [pool.putRequest(req) for req in reqs]
            pool.wait()
            args.clear()
        else:  # single thread
            #post_except(url, data_list)
            for d in data_list:
                # db.put_data(d)
                # continue
                res = post_except(url, d, is_json)
    except Exception:
        raise


# post callback
# def finished(*args):
#     global SUCCESS_COUNT
#     print("finished  ",args)
#     if args[1]:
#         print(args[1])
#         if args[1].status_code == 201:
#             SUCCESS_COUNT += 1
#         else:
#             log.log_error("post data failed\ncode:%d\nresponse:%s\npost_data:%s"
#                           % (args[1].status_code, args[1].text, args[0]))


# no exception handle, for implement retrying
@retry(stop_max_attempt_number=config.retry_http,
       wait_exponential_multiplier=config.slience_http_multiplier*1000,
       wait_exponential_max=config.slience_http_multiplier_max*1000)
def post_retry(url, data, is_json=False):
    try:
        if is_json:
            print("try…json… ", end="")
            j = json.dumps(data)
            print(type(j))
            return requests.post(url, json=json.dumps(data), timeout=config.timeout_http)
        else:
            print("try…str… ", end="")
            return requests.post(url, data=data, timeout=config.timeout_http)
    except Exception as e:
        print(str(e))
        raise


# have exception handle, for implement multi thread
def post_except(url, data, is_json=False):
    global SUCCESS_COUNT
    print("post_except:", url)
    try:
        res = post_retry(url, data, is_json)
        if res.status_code == 201:
            SUCCESS_COUNT += 1
        else:
            log.log_error("post data failed\ncode:%d\nresponse:%s\npost_data:%s"
                          % (res.status_code, res, data))
        return res
    except Exception as e:
        log.log_error("server error:" + str(e) + "\ndata:" + str(data))
        raise

