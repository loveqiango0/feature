#coding=utf8
import pandas as pd
from sql_support import *
import numpy as np
import matplotlib.pylab as plt

# 回测开始时间
begin = '2011-01-01'
# 回测结束时间
end = '2017-01-01'
# 回测股票 or 股票池
stock = "000002"
# 起始资金
global cash
cash = 1000000.00


def position(sigle,df):
    # 初始化仓位，资产
    global cash
    position_now = pd.DataFrame(columns=["position", "type", "time"])
    position_dict = {"position": 0, "time": df.index[0], "type": "init",
                     "trade_price": 0, "return": 0, "cost": 0}
    position_now = position_now.append(pd.Series(position_dict, name=df.index[0]))

    asset = pd.DataFrame()
    # 定义上个交易日的信号和价格
    last_sigle=0
    last_price=0
    for trade_time in sigle.index:

        # 获取今天的信号
        trade_sigle = sigle.loc[trade_time]
        # 获取今天一手股票（100股）的收盘价格
        price_now = sr_avg.loc[trade_time]
        price_hand = price_now*100
        # 获取今天的资产总额
        now_asset = cash+position_now["position"][-1]*price_hand
        # 获取今天的收益率
        rate = now_asset/1000000.00

        # 将资产总额和收益率存入dataframe里
        dict = {"asset": now_asset, "rate_of_return": rate, "time": trade_time}
        asset = asset.append(pd.Series(dict,name=trade_time),ignore_index=False)

        # 如果上一个交易日 发出了买卖信号，则操作
        if last_sigle > 0:
            # 如果当前已经持仓，则忽略此信号
            if not position_now["position"][-1] == 0:
                last_sigle = trade_sigle
                last_price = price_now
                continue

            # 当前股价状态（停牌、涨跌停无法买入）  最高价等于最低价
            state = df.loc[trade_time,"state"]
            if state == 0:
                if price_now > last_price:
                    # 涨停无法买入
                    last_sigle = trade_sigle
                    last_price = price_now
                    continue

            position_dict = {"position": cash//price_hand,"time":trade_time,"type":"buy",
                             "trade_price":cash//price_hand * price_hand,
                             "return":0,"cost":cash}
            position_now=position_now.append(pd.Series(position_dict, name=trade_time))
            cash = cash-cash//price_hand * price_hand

        elif last_sigle < 0:
            if position_now["position"][-1] == 0:
                last_sigle = trade_sigle
                last_price = price_now
                continue

            # 当前股价状态（停牌、涨跌停无法卖出）  最高价等于最低价
            state = df.loc[trade_time, "state"]
            if state == 0:
                if price_now < last_price:
                    # 跌停无法卖出
                    last_sigle = trade_sigle
                    last_price = price_now
                    continue

            cash = cash + position_now["position"][-1] * price_hand
            position_dict = {"position": 0, "time": trade_time,"type":"sell",
                             "trade_price":position_now["position"][-1] * price_hand,
                             "return":(cash/position_now["cost"][-1])-1,"cost":0}
            position_now = position_now.append(pd.Series(position_dict, name=trade_time))

        last_sigle = trade_sigle
        last_price = price_now

    dict={"asset":asset,"position":position_now}
    return dict


if __name__ == "__main__":
    plt.figure(1)
    plt.figure(2)

    ax1 = plt.subplot(211)  # 在图表2中创建子图1
    ax2 = plt.subplot(212)  # 在图表2中创建子图2

    # 回测 数据准备
    sql= "select transtime,close,high,low,volume,amount from data_market_1day where name=%s and " \
         "transtime between '%s' and '%s' order by transtime" % (stock, begin, end)

    df = pd.read_sql(sql,engine,index_col="transtime")
    df["state"]=df["high"]-df["low"]
    df["avg"]=df["amount"]/df["volume"]
    sr_avg = df["avg"]
    sr_avg.dropna(inplace=True)
    ma1 = 12
    ma2 = 60
    mv_avg1 = pd.Series()
    mv_avg2 = pd.Series()

    for step in range(len(sr_avg.index)):
        mv_avg_1 = pd.Series(sr_avg.iloc[step:step + ma1].mean(),index=[sr_avg.iloc[step:step + ma1].index[-1]])
        mv_avg_2 = pd.Series(sr_avg.iloc[step:step + ma2].mean(),index=[sr_avg.iloc[step:step + ma2].index[-1]])
        if step < len(sr_avg.index) - (ma1-1):
            mv_avg1 = mv_avg1.append(mv_avg_1)
        if step<len(sr_avg.index)-(ma2-1):
            mv_avg2 = mv_avg2.append(mv_avg_2)

    sigle = mv_avg1 - mv_avg2
    sigle=sigle.fillna(0)

    plt.figure(2)
    plt.sca(ax1)
    plt.title("feature")
    plt.xlabel("transtime")
    mv_avg1.plot(kind='line', color='g', alpha=1, grid=True)
    mv_avg2.plot(kind='line', color='r', alpha=1, grid=True)

    plt.sca(ax2)  # 选择图表2的子图2
    plt.title("sigle")
    plt.xlabel("transtime")
    sigle.plot(kind='line', color='g', alpha=1, grid=True)

    plt.figure(1)
    plt.title("rate_of_return")
    plt.ylabel("return")
    plt.xlabel("transtime")
    dict=position(sigle,df)
    asset=dict["asset"]
    position=dict["position"]
    # 胜率 win_rate  type:float
    a=position[position["type"]=="sell"]
    win_rate=float(str(a[a["return"]>0.0].shape).split(",")[0][1:])/float(str(a.shape).split(",")[0][1:])
    # 收益率 sr_avg_rate   type:series
    rate=asset["rate_of_return"]
    sr_avg_rate=sr_avg/sr_avg[0]
    sr_avg_rate.plot(kind='line', color='r', alpha=1, grid=True,use_index=False)
    rate.plot(kind='line', color='b', alpha=1, grid=True,use_index=False)
    plt.show()
