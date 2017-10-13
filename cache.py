import io
import sys
import os
import collections


class Cache:
    def __init__(self, path="", type="kv"):
        """
        :param path: cache文件路径
        :param type: 类型：kv型
        """
        if not os.path.exists(path):
            open(path,"w", encoding="utf-8").close()
        self.path = path

    def read_cache(self):
        """
        读取全部缓存
        :return: dict
        """
        odict = collections.OrderedDict()
        with open(self.path, 'r+', encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                line = line.replace("\n", "")
                line = line.split(" ")
                odict[line[0]] = line[1]
        return odict

    def write_cache(self, data, default="0"):
        """
        写缓存
        :param data: 数据，dict|list
        :param default: 为list时指定的默认值
        :return: 成功
        """
        lines = ""
        for d in data:
            if isinstance(data, dict):
                lines += d + " " + data[d] + "\n"
            elif isinstance(data, list):
                lines += d + " " + default + "\n"
        with open(self.path, 'w', encoding="utf-8") as f:
            f.write(lines)
            return True

    # data为list时需要指定value的default值
    def update_cache(self, data, default="0"):
        """
        增量添加缓存，重复的key的将忽略
        :param data: 数据
        :param default: 
        :return: 
        """
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

    def remove_item(self, key):
        dbdict = collections.OrderedDict()
        try:
            with open(self.path, 'r+', encoding='utf-8') as f:
                lines = f.readlines()
                re = False
                for line in lines:
                    line = line.replace("\n", "")
                    line = line.split(" ")
                    if line[0] != str(key):
                        dbdict[line[0]] = line[1]
                    else:
                        re = True
                f.seek(0)
                f.truncate()
                lines = ""
                for l in dbdict:
                    lines += l + " " + dbdict[l] + "\n"
                f.write(lines)
                return re
        except Exception as e:
            raise e

    def get_value(self, key, then="rm|set=1"):
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

c = Cache("tmp/list_cache_20170929.txt")
# re = c.remove_item("nqhq.dbf.091049")
# print(re)