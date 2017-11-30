import os
import sqlite3
import time

from .log import Log, view_bar
from . import config
from .map_dict import map_dict
from .read import Read
from .commit import Commit


def to_dict(df):
    dl = []
    for row in df.iterrows():
        d = row[1].to_dict()
        dl.append(d)
    return dl


def run():
    print("===== Start upload =====")
    l = Log()
    req = Commit(retry_http=config.retry_http,
                 silence_http_multiplier=config.silence_http_multiplier,
                 silence_http_multiplier_max=config.silence_http_multiplier_max,
                 timeout_http=config.timeout_http)
    while True:
        if not os.path.exists(config.dbf_cache):
            time.sleep(10)
            continue
        try:
            r = Read(config.dbf_cache)
            data = r.select_data(where="status=0", limit=config.max_upload)
            data = to_dict(data)
            data = map_dict(data,
                            config.map_rule['map'],
                            config.map_rule['strict'],
                            config.map_rule['lower'],
                            swap=config.map_rule['swap'])
            data = None
            if data:
                req.commit_data_list(post_url=config.api_post,
                                     data_list=data,
                                     enable_thread=config.enable_thread,
                                     thread_pool_size=config.thread_pool_size)

                total = r.exe_sql("select count(*) as count from nqhq")
                uploaded_count = r.exe_sql("select count(*) as count from nqhq WHERE status=1")
                total = total.ix[0, 0]
                uploaded_count = uploaded_count.ix[0, 0]
                view_bar(uploaded_count, total)

            else:
                # 检测
                # data = r.select_data(where="status=1 and HQZQDM!='000000'", limit=config.max_upload)
                # data = to_dict(data)
                # data = map_dict(data,
                #                 config.map_rule['map'],
                #                 config.map_rule['strict'],
                #                 config.map_rule['lower'],
                #                 swap=config.map_rule['swap'])
                # req.verify_data_list(data)
                # if data:
                #     pass
                time.sleep(1)

        except Exception as e:
            l.log_error(str(e))
