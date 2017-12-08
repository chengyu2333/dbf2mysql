import time
import sqlite3
from pandas import concat
from retrying import retry


class Process:
    """
    处理dataframe数据
    """
    def __init__(self):
        pass

    def drop_duplicate(self, df_last, df):
        if df_last is not None and not df_last.empty:
            l = len(df_last)
        else:
            l = 0
        df = concat([df_last, df], ignore_index=True).drop_duplicates().ix[l:, :]
        return df

    def to_dict(self, df):
        dl = []
        for row in df.iterrows():
            d = row[1].to_dict()
            dl.append(d)
        return dl

    @retry(stop_max_attempt_number=3,
           wait_fixed=1000)
    def to_sql(self, df, db_path):
        conn = sqlite3.connect(db_path)
        
        # if_exists : {‘fail’, ‘replace’, ‘append’}
        df.insert(len(df.columns), "status", 0)
        try:
            df.to_sql("nqhq", conn, index=True, flavor="sqlite", if_exists="append")
        except Exception as e:
            raise e

    def convert(self, df):
        # 转换数据
        # 新增updated_at列
        try:
            up_data = df[df['HQZQDM'] == "000000"]['HQZQJC'].values[0]
            up_time = df[df['HQZQDM'] == "000000"]['HQCJBS'].values[0]
        except Exception:
            return(df)
        updated_at = str(up_data) + str(up_time)
        updated_at = time.strptime(updated_at, "%Y%m%d%H%M%S")
        updated_at = time.strftime("%Y-%m-%dT%H:%M:%S", updated_at)
        df.insert(len(df.columns), "updated_at", updated_at)

        # 降低精度
        df = df.round(2)
        return df

    def filter(self, df):
        # 剔除数据
        i = df[df['HQZQDM']=="899001"].index
        j = df[df['HQZQDM']=="000000"].index
        if not i.empty:
            df = df.drop([i[0]])
        if not j.empty:
            df = df.drop([j[0]])
        return df

    def process(self, df_last, df):
        # 顺序不能乱
        data = self.drop_duplicate(df_last, df)
        data = self.convert(data)
        data = self.filter(data)
        return data

    def first(self, df):
        # 提取第一个文件的信息
        data = df.query("HQZQDM=='899001' | HQZQDM=='000000'")
        data = self.convert(data)
        data = data.drop(0)
        return data
