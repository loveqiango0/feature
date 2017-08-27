#coding=utf8
import pandas as pd
from sql_support import *

# 回测开始时间
begin = '2013-01-01'
# 回测结束时间
end = '2016-01-01'
# 回测股票 or 股票池
stock = "000002.SZ"

# 回测数据准备
sql = "select transtime,close,high,low,volume,amt from %s where name='%s' and " \
      "transtime between '%s' and '%s' order by transtime" % (dbTable, stock, begin, end)
sql1 = "select close,date from get_index where date between '%s' and '%s' order by date" % (begin, end)

df = pd.read_sql(sql, engine, index_col="transtime")
get_index = pd.read_sql(sql1, engine)
get_index.set_index("date")

df["state"] = df["high"] - df["low"]
df["avg"] = df["amt"] / df["volume"]
sr_avg = df["avg"]
sr_avg.dropna(inplace=True)
n1 = 12
n2 = 26
n3 = 9
ema_1=sr_avg[0]
ema_2=sr_avg[0]
ema1 = pd.Series()
ema2 = pd.Series()
diff = pd.Series()
for step in range(len(sr_avg.index)):
    ema_1=ema_1
    ema_2=ema_2
    ema_1 = pd.Series(ema_1, index=[sr_avg.iloc[step:step + n1].index[-1]])
    ema_2 = pd.Series(ema_2, index=[sr_avg.iloc[step:step + n2].index[-1]])
    diff_1= pd.Series(sr_avg.iloc[step:step + n2].mean(), index=[sr_avg.iloc[step:step + n2].index[-1]])
    if step < len(sr_avg.index) - (n1 - 1):
        ema1 = ema1.append(ema_1)
    if step < len(sr_avg.index) - (n2 - 1):
        ema2 = ema2.append(ema_2)




bar=(diff-dea)*2
sigle=bar
sigle = sigle.fillna(0)