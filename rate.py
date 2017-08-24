#coding=utf8
import pandas as pd
import numpy as np
from sql_support import *
import matplotlib.pylab as plt


def register():
    return {'':'rate'}


def calcFeature(dict_series):
    # 周期
    N = 1
    sr_avg = dict_series['avg']
    sr_avg.fillna(0, inplace=True)
    sr_rate = pd.Series()
    pre_price=sr_avg[0]
    for step in range(0,len(sr_avg.index)):
        price_now = sr_avg.iloc[step+N]
        rate = pd.Series(np.log(price_now/pre_price),index=sr_avg.index[step+N])
        sr_rate = sr_rate.append(rate)

    return sr_rate

if __name__=="__main__":
    plt.figure(1)
    plt.subplot(211)  # 在图表2中创建子图1

    N = 1
    sql="select amount,volume,transtime from data_market_1day where name='000002' and transtime between '2012-01-01' and '2016-12-01'"
    df=pd.read_sql(sql,engine,index_col="transtime")
    df["avg"]=df["amount"]/df["volume"]
    sr_avg=df["avg"]
    sr_avg.dropna(inplace=True)
    sr_rate = pd.Series()
    df_volatilily = pd.DataFrame()
    pre_price = sr_avg[0]
    for step in range(0, len(sr_avg.index)-1):
        price_now = sr_avg.iloc[step + N]
        rate = pd.Series(np.log(price_now / pre_price), index=[sr_avg.index[step + N]])
        sr_rate = sr_rate.append(rate)

    sr_rate.plot(kind='line', color='g', alpha=1, grid=True)

    plt.subplot(212)  # 在图表2中创建子图2
    N = 10
    for step in range(0, len(sr_rate.index)-N+1):
        sr_avg_1 = sr_rate.iloc[step:step + N]
        volatilily = np.std(sr_avg_1)*100*np.sqrt(242)
        dict = {"volatilily": volatilily, "time": sr_avg_1.index[-1]}
        print dict["time"]
        df_volatilily = df_volatilily.append(pd.Series(dict, name=sr_avg_1.index[-1]),ignore_index=False)

    sr_volatilily = df_volatilily["volatilily"]
    sr_volatilily.plot(kind='line', color='r', alpha=1, grid=True)

    plt.show()
