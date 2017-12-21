import sqlite3
import time
import pandas
import sys
path = "data/cache_%s.sqlite" % time.strftime("%Y%m%d")
pandas_format = True
print("===== SQLite Simple Shell =====")
print(path)
print("r: set all status=0")
print("a: select all")
print("q: quit")
print()
while True:
    sys.stdout.write("\033[1;32m")
    sql = input("SQL >")
    sys.stdout.write("\033[1m")
    if sql == "q":
        exit()
    if sql == "r":
        sql = "update nqhq set status=0"
    if sql == "a":
        sql = "select * from nqhq"

    try:
        conn = sqlite3.connect(path)
        if pandas_format and sql[0:6] == "select":
            re = pandas.read_sql_query(sql, conn)
            print(re)
        else:
            re = conn.execute(sql)
            conn.commit()
            print(re.fetchall())
    except Exception as e:
        print(e)
        continue
    finally:
        conn.close()
