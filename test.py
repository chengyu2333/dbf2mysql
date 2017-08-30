# encode: utf-8
import os
from dbfread import DBF
from urllib import request

url = "http://183.60.7.32/nqhq.dbf"
if os.path.exists("nqhq.dbf"):
    os.remove("nqhq.dbf")


request.urlretrieve(url,"nqhq.dbf")
filename = "nqhq.dbf"
mtime = os.stat(filename).st_mtime
ctime = os.stat(filename).st_ctime

print(mtime," ",ctime)

pass

table = DBF(filename,char_decode_errors="ignore")
print(len(table))
for record in table:
    for field in record:
        print(field," ", end="")
    print()
    break
for record in table:
    for field in record:
        print(field, "=", record[field], end = ",")
    print()
    break
