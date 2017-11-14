# -*- coding: utf-8 -*
import io
import sys
import os
import collections


class Cache:
    def __init__(self, path=""):
        if not os.path.exists(path):
            open(path, "w", encoding="utf-8").close()
        self.path = path

    def __save_file(self, path, odict, sort=True):
        if sort:
            odict = self.__sort(odict, False)
        with open(path, 'w', encoding="utf-8") as f:
            f.seek(0)
            f.truncate()
            lines = ""
            for od in odict:
                lines += od + " " + odict[od] + "\n"
            f.write(lines)
            return True

    @staticmethod
    def __read_file(path):
        odict = collections.OrderedDict()
        if not os.path.exists(path):
            return None
        with open(path, 'r', encoding="utf-8") as f:
            lines = f.readlines()
        # 源数据加载到OrderedDict
        for line in lines:
            line = line.replace("\n", "")
            line = line.split(" ")
            odict[line[0]] = line[1]
        return odict

    @staticmethod
    def __sort(data, desc=True):
        if desc:
            return collections.OrderedDict(sorted(data.items(), key=lambda t: t[0], reverse=True))
        else:
            return collections.OrderedDict(sorted(data.items(), key=lambda t: t[0]))

    def read_all(self):
        return self.__read_file(self.path)

    def write_all(self, data, default="0"):
        """
        写缓存
        :param data: 数据，dict|list
        :param default: 为list时需要指定的默认值
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
    def update_all(self, data, default="0"):
        """
        增量添加缓存，重复的key的将忽略
        :param data: dict | list
        :param default: data为list时指定的默认值
        :return: 
        """
        odict = collections.OrderedDict()
        with open(self.path, 'r+', encoding="utf-8") as f:
            lines = f.readlines()
            # 源数据加载到OrderedDict
            for line in lines:
                line = line.replace("\n", "")
                line = line.split(" ")
                odict[line[0]] = line[1]
            # 遍历映射新数据
            for item in data:
                # 新数据不在源数据中，添加
                if item not in odict and isinstance(data, dict):
                    odict[item] = data[item]
                elif item not in odict and isinstance(data, list):
                    odict[item] = default
            # 清空写入缓存文件
            f.seek(0)
            f.truncate()
            lines = ""
            for od in odict:
                lines += od + " " + odict[od] + "\n"
            f.write(lines)
        pass

    def append(self, key, value):
        """
        追加一条记录
        :param key: 
        :param value: 
        :return: 
        """
        with open(self.path, "a+", encoding="utf-8") as f:
            f.write(str(key) + " " + str(value) + "\n")
            return True

    def update(self, key, value, auto_append=True):
        """
        按key更新数据
        :param key: 
        :param value: 
        :return: 
        """
        try:
            data = self.__read_file(self.path)
            if key in data:
                data[key] = value
                self.__save_file(self.path, data)
                return True
            else:
                if auto_append:
                    data[key] = value
                    self.__save_file(self.path, data)
                    return True
                else:
                    return False
        except Exception as e:
            raise

    def get_key(self, value, reverse=False):
        """
        根据value获取一个key
        :param value: 
        :param reverse: 倒序获取
        :return: 
        """
        dbdict = collections.OrderedDict()
        try:
            with open(self.path, 'r+', encoding="utf-8") as f:
                lines = f.readlines()
                list_tmp = []

                # 源数据读入到list_tmp中
                for line in lines:
                    list_tmp.append(line)
                # 倒序
                if reverse:
                    list_tmp.reverse()

                # list_tmp读入到dbdict中
                for line in list_tmp:
                    line = line.replace("\n", "")
                    line = line.split(" ")
                    dbdict[line[0]] = line[1]

                # 如果要查找的值在dbdict中
                if value in dbdict.values():  # if record have flag 0
                    keys = list(dbdict.keys())
                    vi = list(dbdict.values()).index(value)
                    dbpath = keys[vi]
                    if vi == 0:
                        dbpath_prev = None
                    else:
                        dbpath_prev = keys[vi - 1]
                    return dbpath, dbpath_prev
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

    def remove(self, key):
        """
        按key删除记录
        :param key: 
        :return: 
        """
        try:
            data = self.__read_file(self.path)
            print(len(data))
            if key in data:
                d = data.pop(key)
                print(len(data))
                return self.__save_file(self.path, data)
            else:
                return False
        except Exception as e:
            raise e

    def sort_by_key(self, desc=True):
        data = self.__read_file(self.path)
        if desc:
            data = collections.OrderedDict(sorted(data.items(), key=lambda t: t[0], reverse=True))
        else:
            data = collections.OrderedDict(sorted(data.items(), key=lambda t: t[0]))
        try:
            self.__save_file(self.path, data, False)
            return True
        except Exception as e:
            raise e

    def reset(self):
        pass
        
    def total(self, value="1"):
        total = 0
        count = 0
        try:
            with open(self.path, 'r', encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines:
                    line = line.replace("\n", "")
                    line = line.split(" ")
                    total += 1
                    if line[1] == str(value):
                        count += 1
                print("total:", total, "count:", count)
        except Exception as e:
            raise

# c = Cache("tmp/list.txt")
# c = Cache("tmp\list_cache_20171114.txt")
# dbpath, dbpath_prev = c.get_key("1")
# print(dbpath)
# print(dbpath_prev)
# c.update(dbpath, "1")
# print(k)
# c.update(k, "0")
#
# for d in c.read_all():
#     print(d)



# re = c.remove_item_by_key("nqhq.dbf.091049")
# print(c.update_by_key("nqhq.dbf.145525", "2"))
# key = c.get_key_by_value("0",reverse=True)
# up = c.update_by_key(key, "1")
# print(key)
# print(up)
# print(c.remove_by_key("nqhq.dbf.152749"))

