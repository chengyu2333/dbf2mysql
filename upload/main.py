import os
import sqlite3
import time

from upload.map_dict import map_dict
import config
from lib.log import Log, view_bar
from upload.upload import Upload
from upload.read import Read


def run():
    u = Upload()
    l = Log()
    while True:
        if not os.path.exists(config.dbf_cache):
            time.sleep(10)
            continue
        r = Read(config.dbf_cache)
        try:
            data = r.select_data("status=0", "100")
            unique = data[['HQZQDM', 'updated_at']]
            data = p.to_dict(data)
            data = map_dict(data,
                            config.map_rule['map'],
                            config.map_rule['strict'],
                            config.map_rule['lower'],
                            swap=config.map_rule['swap'])
            if data:
                u.upload(data)
                conn = sqlite3.connect(config.dbf_cache)
                cur = conn.cursor()
                purchases =[]
                for row in unique.iterrows():
                    purchases.append((row[1]['HQZQDM'], row[1]['updated_at']))
                    # cur.execute("update %s set status=1 WHERE HQZQDM='%s' and updated_at='%s'"
                    #             % ("nqhq", row[1]['HQZQDM'], row[1]['updated_at']))
                if purchases:
                    cur.executemany("update nqhq set status=1 WHERE HQZQDM=? and updated_at=?", purchases)
                    conn.commit()
                    total = r.exe_sql("select count(*) as count from nqhq")
                    count = r.exe_sql("select count(*) as count from nqhq WHERE status=1")
                    total = total.ix[0, 0]
                    count = count.ix[0,0]
                    view_bar(count, total)

            else:
                time.sleep(1)

        except Exception as e:
            l.log_error(str(e))
