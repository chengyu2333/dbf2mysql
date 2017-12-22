import os
import time

from .log import Log, view_bar
from . import config
from .map_dict import map_dict
from .commit import Commit
from .db import SessionManager
from . import model
from sqlalchemy.exc import OperationalError


def run():
    print("===== Start Upload =====")
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
            session = SessionManager().get_session()
            # 升序获取，保证按时间序列同步
            data = session.query(model.Nqhq)\
                .order_by(model.Nqhq.updated_at.asc())\
                .filter(model.Nqhq.status == 0)\
                .limit(config.max_upload)
            data = map_dict(data,
                            config.map_rule['map'],
                            config.map_rule['strict'],
                            config.map_rule['lower'],
                            swap=config.map_rule['swap'])

            if data:
                # 上传数据
                req.commit_data_list(post_url=config.api_post,
                                     data_list=data,
                                     enable_thread=config.enable_thread,
                                     thread_pool_size=config.thread_pool_size)

                view_bar(session.query(model.Nqhq).filter(model.Nqhq.status >= 1).count(),
                         session.query(model.Nqhq).count())
                print(" failed:", session.query(model.Nqhq).filter(model.Nqhq.status == -1).count(), end="")
                print(" current:", data[-1]['updated_at'],
                      " now:", time.strftime("%Y-%m-%d %H:%M:%S"),
                      " count:", str(len(data)), end="")

            else:
                # 校验数据
                data = session.query(model.Nqhq)\
                    .filter(model.Nqhq.status != 0, model.Nqhq.api_id != "")\
                    .order_by(model.Nqhq.status.asc())\
                    .limit(5)
                for d in data:
                    print("verify:", req.verify_data(d.api_id), " ", d.api_id, "\r",  end="")
                else:
                    time.sleep(5)
        except OperationalError as e:
            if "locked" in str(e):
                pass
            else:
                l.log_error(str(e))
        except Exception as e:
            l.log_error(str(e))
        finally:
            session.close()
