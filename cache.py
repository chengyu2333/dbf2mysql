import io
import sys
import os
import collections


class Cache:
    def __init__(self, path="", type="kv"):
        if not os.path.exists(path):
            open(path,"w", encoding="utf-8").close()
        self.path = path

    # return dict
    def read_cache(self):
        odict = collections.OrderedDict()
        with open(self.path, 'r+', encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                line = line.replace("\n", "")
                line = line.split(" ")
                odict[line[0]] = line[1]
        return odict

    def write_cache(self, data, default="0"):
        lines = ""
        for d in data:
            if isinstance(data, dict):
                lines += d + " " + data[d] + "\n"
            elif isinstance(data, list):
                lines += d + " " + default +"\n"
        with open(self.path, 'w', encoding="utf-8") as f:
            f.write(lines)

    # data为list时需要指定value的default值
    def update_cache(self, data, default ="0"):
        odict = collections.OrderedDict()
        with open(self.path, 'r+', encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                line = line.replace("\n", "")
                line = line.split(" ")
                odict[line[0]] = line[1]
            for item in data:
                if item not in odict and isinstance(data, dict):
                    odict[item] = data[item]
                elif item not in odict and isinstance(data, list):
                    odict[item] = default
            f.seek(0)
            f.truncate()
            lines = ""
            for od in odict:
                lines += od + " " + odict[od] + "\n"
            f.write(lines)
        pass

    def put_item(self, key, value):
        with open(self.path, "a+", encoding="utf-8") as f:
            f.write(str(key) + " " + str(value) + "\n")
            return True

    # return tuple
    def pop_item_v(self, get_value="0", set_value="1"):
        dbdict = collections.OrderedDict()
        try:
            with open(self.path, 'r+', encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines:
                    line = line.replace("\n", "")
                    line = line.split(" ")
                    dbdict[line[0]] = line[1]
                if get_value in dbdict.values():  # if record have flag 0
                    dbpath = list(dbdict.keys())[list(dbdict.values()).index(get_value)]
                    dbdict[dbpath] = set_value
                    f.seek(0)
                    f.truncate()
                    lines = ""
                    for l in dbdict:
                        lines += l + " " + dbdict[l] + "\n"
                    f.write(lines)
                    return dbpath
        except Exception as e:
            raise

    def get_value(self, key):
        try:
            with open(self.path, 'r+', encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines:
                    line = line.replace("\n", "")
                    line = line.split(" ")
                    if line[0] == str(key):
                        return line[1]
                else:
                    return None
        except Exception as e:
            raise

# c = Cache("tmp/list_cache_20170928.txt")
# print(c.read_cache())
# c.update_dblist_cache("tmp/dblist_cache.txt","dbf")