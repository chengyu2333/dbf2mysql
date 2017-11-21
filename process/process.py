import time
import sqlite3
from pandas import concat
from lib.retry import retry


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

    @retry(stop_max_attempt_number=3)
    def convert(self, df):
        up_data = df[df['HQZQDM'] == "000000"]['HQZQJC'].values[0]
        up_time = df[df['HQZQDM'] == "000000"]['HQCJBS'].values[0]
        updated_at = str(up_data) + str(up_time)
        updated_at = time.strptime(updated_at, "%Y%m%d%H%M%S")
        updated_at = time.strftime("%Y-%m-%dT%H:%M:%S", updated_at)
        df.insert(len(df.columns), "updated_at", updated_at)
        return df

    def filter(self, df):
        # 剔除数据
        i = df[df['HQZQDM']=="899001"].index
        if not i.empty:
            df = df.drop([df[df['HQZQDM']=="899001"].index[0]])
        # 降低精度
        df = df.round(2)
        return df

    def process(self, df_last, df):
        data = self.drop_duplicate(df_last, df)
        data = self.filter(data)
        data = self.convert(data)
        return data
