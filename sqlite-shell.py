import sqlite3
import time
import pandas
import sys
path = "data/cache_%s.sqlite" % time.strftime("%Y%m%d")
pandas_format = True
print("===== SQLite Simple Shell =====")
print(path)
while True:
    sys.stdout.write("\033[1;32m")
    sql = input("SQL:")
    sys.stdout.write("\033[1m")
    if sql == "q":
        exit()
    try:
        conn = sqlite3.connect(path)
        if pandas_format and sql[0:6] == "select":
            re = pandas.read_sql_query(sql, conn)
            print(re)
        else:
            re = conn.execute(sql)
            conn.commit()
            print(re.fetchall())
        conn.close()
    except Exception as e:
        print(e)
        continue
