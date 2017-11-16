# -*- coding: utf-8 -*
from req import GetReq


get = GetReq()
list = get.get_db_file()

print(list)