# -*- coding: utf-8 -*
import os
import time
import requests
import json
import io


def update_dblist(dblist_path, dbfile_path):
    try:
        dblist = os.listdir(dbfile_path)
        print("file total:", len(dblist))
        dbdict = {}
        lines = ""
        if os.path.exists(dblist_path):
            with open(dblist_path, 'r+', encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines:
                    line = line.replace("\n", "")
                    line = line.split(" ")
                    dbdict[line[0]] =line[1]
                for l in dblist:
                    if l not in dbdict:
                        dbdict[l] = "0"
                f.seek(0)
                f.truncate()
                lines = ""
                for l in dbdict:
                    lines += l + " " + dbdict[l] + "\n"
                f.write(lines)
        else:
            lines =  ""
            for l in dblist:
                lines += l + " " + "0\n"
            with open(dblist_path, 'w', encoding="utf-8") as f:
                f.write(lines)
    except:
        raise

# cache file list and pop File path
def pop_dbpath(dbfile_path):
    dblist_path = "tmp/dbdict.txt"
    dbdict = {}
    try:
        update_dblist(dblist_path, dbfile_path)
        with open(dblist_path, 'r+', encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                line = line.replace("\n", "")
                line = line.split(" ")
                dbdict[line[0]] = line[1]
            if "0" in dbdict.values():
                dbpath = list(dbdict.keys())[list(dbdict.values()).index("0")]
                dbdict[dbpath] = "1"
                f.seek(0)
                f.truncate()
                lines = ""
                for l in dbdict:
                    lines += l + " " + dbdict[l]+ "\n"
                f.write(lines)
                return dbfile_path + dbpath
    except Exception as e:
        raise

while 1:
    p = pop_dbpath("dbf/")
    if p:
        print(p)
    else:
        print("finished")
        break


def get():
    path = "tmp/nqhq.dbf"
    time_temp_path = "tmp/old_time.tmp"
    if os.path.isfile(path):
        create_time = os.stat(path).st_ctime
        if os.path.exists(time_temp_path):
            f = open(time_temp_path, 'r+')
            create_time_old = f.read()
            create_time_old = float(create_time_old) if create_time_old else False
        else:
            create_time_old = False
        f = open(time_temp_path, 'w')
        f.write(str(create_time))
        f.close()
        if not create_time_old or create_time_old < create_time:
            return path
        else:
            return False
        return path

# print(get())


def get_id(code=833027):
    code = str(code)
    id_temp_path = "tmp/id_cache.txt"
    api_url = "http://api.chinaipo.com/markets/v1/rthq/?code=" + code
    id_list = {}
    # get id from cache
    if os.path.exists(id_temp_path):
        f = open(id_temp_path, "r")
        id_temp = f.read()
        f.close()
        if id_temp:
            id_list = json.loads(id_temp)
            if code in id_list:
                return id_list[code]
    # get id from api
    response = requests.get(api_url)
    result = json.loads(response.text)
    if result['results']:
        result = result['results'][0]['id']
        f = open(id_temp_path, "w")
        id_list[code] = result
        f.write(json.dumps(id_list))
        f.close()
        return result
    else:
        return False

def update_date(id, data):
    api_url = "http://api.chinaipo.com/markets/v1/rthq/%s/" % id
    response = requests.put(api_url,data)
    print(response)
    print(response.text)

# update_date("59bfcbb99c94dd39d01bee39",{"hqzqjc":"东金科技"})
# print(get_id())

time.sleep(5)