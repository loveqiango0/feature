#coding=utf8
import pandas as pd
from sql_support import *
import matplotlib.pylab as plt
import datetime

# 回测开始时间
begin = '2012-01-01'
# 回测结束时间
end = '2017-01-01'
# 回测股票 or 股票池
stocks = ["000001","000002","600652"]
dbTable = "data_market_1day"
cash = 1000000.00
# 回测数据准备
sql = "select transtime,name,close,high,low,amount from %s where " \
      "transtime between '%s' and '%s' order by transtime" % (dbTable, begin, end)

sql1 = "select close,date from get_index where date between '%s' and '%s' order by date" % (begin, end)

df_all = pd.read_sql(sql, engine, index_col="transtime")
get_index = pd.read_sql(sql1, engine, index_col="date")

df_all["state"] = df_all["high"] - df_all["low"]
global position_now
position_now = pd.DataFrame(columns=["position", "type", "time"])
position_dict = {"position": 0.0, "time": get_index.index[0], "type": "init",
                 "return": 0.0, "cost": 0.0,"trade_rate":0.0}
for stock in stocks:
    position_now = position_now.append(pd.Series(position_dict,name=stock))
for stock in stocks:
    position_now = position_now.append(pd.Series(position_dict,name=stock))

asset = pd.DataFrame(columns=["asset","rate_of_return","reback"],index=[get_index.index[0]])
asset=asset.fillna(0)

def order_buy(stock, one_hands_price, hands, transtime):
    global position_now
    position_dict = {"position": hands, "time": transtime, "type": "buy",
                     "return": 0, "cost": hands*one_hands_price,"trade_rate":0}
    position_now = position_now.append(pd.Series(position_dict, name=stock))


def order_sell(stock,one_hands_price,transtime,):
    global position_now
    position=position_now.loc[stock, "position"][-1]
    cost = position_now.loc[stock, "cost"][-1]
    trade_rate=((one_hands_price*position)/cost) - 1
    position_dict = {"position": 0, "time": transtime, "type": "sell",
                     "return":one_hands_price*position, "cost": 0,"trade_rate":trade_rate}
    position_now = position_now.append(pd.Series(position_dict, name=stock))
    return position

if __name__ == "__main__":
    last_data = pd.DataFrame(columns=["ema1", "ema2", "dea"])
    bar_frame = pd.DataFrame(columns=["bar", "transtime"], index=stocks*2)
    bar_frame = bar_frame.fillna(0)
    n1, n2, n3 = (12, 26, 9)

    for transtime in get_index.index.tolist():
        # 获取今天的资产总额
        asset_today = 0.00
        reback = 0.00
        for stock in stocks:
            df = df_all[df_all.name == stock]
            if transtime not in df.index:
                while True:
                    transtime=transtime-datetime.timedelta(days=1)
                    if transtime in df.index:
                        close = df.loc[transtime, "close"]
                        asset_today += close*100 * int(position_now.loc[stock, "position"][-1])
                        break
                continue
            close = df.loc[transtime, "close"]
            if stock not in last_data.index:
                ema_1, ema_2, dea = [close] * 3
            else:
                ema_1=last_data.loc[stock,"ema1"]
                ema_2 = last_data.loc[stock, "ema2"]
                dea = last_data.loc[stock, "dea"]

            ema_1 = ema_1 * (n1 - 1) / (n1 + 1) + close * 2 / (n1 + 1)
            ema_2 = ema_2 * (n2 - 1) / (n2 + 1) + close * 2 / (n2 + 1)

            last_data.loc[stock, "ema1"] = ema_1
            last_data.loc[stock, "ema2"] = ema_2

            diff = ema_1 - ema_2
            dea = dea * (n3 - 1) / (n3 + 1) + diff * 2 / (n3 + 1)
            last_data.loc[stock, "dea"] = dea

            bar = (diff - dea) * 2
            one_hands_price = 100 * close
            if bar_frame.loc[bar_frame.index==stock,"bar"][-1] > 0:
                if bar_frame.loc[bar_frame.index == stock, "bar"][-2] < 0:

                    hands = (cash/len(stocks))//one_hands_price
                    order_buy(stock, one_hands_price, hands, transtime)
                    cash=cash-hands*one_hands_price

            if bar_frame.loc[bar_frame.index==stock,"bar"][-1] < 0:
                if bar_frame.loc[bar_frame.index == stock, "bar"][-2] > 0:
                    hands = order_sell(stock,one_hands_price,transtime)
                    cash = cash + hands * one_hands_price

            dict = {"transtime":transtime,"bar":bar}
            bar_frame=bar_frame.append(pd.Series(dict,name=stock),ignore_index=False)

            # 一天结算一次
            asset_today += one_hands_price * int(position_now.loc[stock,"position"][-1])

        asset_today += cash
        # 获取今天的收益率
        rate = asset_today / 1000000.00
        # 回撤
        reback = 1 - (asset_today / max(asset["asset"]))

        # 将资产总额和收益率存入dataframe里
        asset_dict = {"asset": asset_today, "rate_of_return": rate, "reback": reback}
        asset = asset.append(pd.Series(asset_dict, name=transtime))

    print asset["rate_of_return"][-1]






