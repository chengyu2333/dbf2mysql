from pandas import concat, DataFrame
from simpledbf import Dbf5
import time

dbf1 = Dbf5('f:prev.dbf', codec='gbk')
dbf2 = Dbf5('f:nqhq.dbf', codec='gbk')

df1 = dbf1.to_dataframe()
df2 = dbf2.to_dataframe()

l = len(df1)

dl = []
df = concat([df1, df2], ignore_index=True).drop_duplicates().ix[l:,:]
t = time.time()
for row in df.iterrows():
	dl.append(row[1].to_dict())
print(time.time()-t)

print(len(dl))
