# coding: utf-8
import decimal
import random
from datetime import datetime

import talib

from models.models import TradingDerivativeIndicator, IncomeStatement, PrimaryFinanceIndicator
from storage.StockDailyBarAdjustPrevDao import StockDailyBarAdjustPrevDao
import math

from storage.StockDao import StockDao
from storage.StockFundamentalsDao import StockFundamentalsDao
import numpy as np
import pandas as pd


class SellStrategies:
    # 卖出策略1：
    #    1. 7%止损线
    #    2. 盈利15%后，止损线提高到5%
    #    3. 之后跌破50日线或者跌到20%止损

    def sellStrategy1(self, buyPrice, bars):
        pass


class BuyPointInvestigation:
    def __init__(self):
        self.stockBarDao = StockDailyBarAdjustPrevDao()
        self.stockFundamentals = StockFundamentalsDao()

    def calculate_pe_heigt_eight_year(self, tradeDate, derivatives):
        '''
        计算8年PE高度, 一年250交易日，一年以内的高度没有可信度，返回0
        :param tradeDate:
        :param derivatives:
        :return:
        '''
        for i in range(len(derivatives)):
            if derivatives[i].end_date == tradeDate:
                n = 0
                m = 0
                for j in range(max(0, i - 2000), i):
                    n += 1
                    if derivatives[j].PETTM < derivatives[i].PETTM:
                        m += 1
                return m / n if i > 250 else 0
        return 0

    def calculate_pb_heigt_eight_year(self, trade_date, derivatives):
        '''
        计算8年PB高度, 一年250交易日. 一年以内的高度没有可信度, 返回0

        :param trade_date:
        :param derivatives:
        :return:
        '''
        for i in range(len(derivatives)):
            if derivatives[i].end_date == trade_date:
                n = 0
                m = 0
                for j in range(max(0, i - 2000), i):
                    n += 1
                    if derivatives[j].PB < derivatives[i].PB:
                        m += 1
                return m / n if i > 250 else 0
        return 0

    def get_derivatives_by_date(self, trade_date, derivatives):
        for i in range(len(derivatives)):
            if derivatives[i].end_date == trade_date:
                return derivatives[i]
        return None

    def get_primary_finance_indicator_by_date(self, trade_date, finance_indicators):
        for i in range(len(finance_indicators) - 1, 0, -1):
            if finance_indicators[i].pub_date < trade_date:
                return finance_indicators[i]
        return None

    def calculate_average_turn_rate(self, start_date, end_date, derivatives):
        '''
        calculate average daily turn rate between start date and end date
        :param start_date:
        :param end_date:
        :param derivatives:
        :return: average turn rate
        '''
        turn_rate = 0
        n = 0
        for i in range(len(derivatives)):
            if derivatives[i].end_date >= start_date and derivatives[i].end_date <= end_date:
                turn_rate += derivatives[i].TURNRATE
                n+=1
        return turn_rate/n if n > 0 else 0

    # 从上市日起比当前价格低的天数
    def calculate_days_with_lower_price(self, bars, pos):
        close = bars[pos].close
        days = 0
        for i in range(pos-1, 0, -1):
            if bars[i].close < close:
                days += 1
        return days

    # 从左侧第一个比pos点高的算起，到pos点的总天数
    def calculate_new_high_days(self, bars, pos):
        close = bars[pos].close
        days = 0
        for i in range(pos - 1, 0, -1):
            if bars[i].close > close:
                break
            days += 1
        return days

    # pos点作为新高点，从最低点上涨的天数
    def calculate_days_from_bottom(self, bars, pos):
        close = bars[pos].close
        minimal = bars[pos].close
        days = 0
        for i in range(pos-1, 0, -1):
            if bars[i].close > close:
                break
            if bars[i].close < minimal:
                minimal = bars[i].close
                days = pos - i

        return days

    def calculate_volume_ratio(self, bars, start, end):
        average_volume = np.mean([bars[i].volume for i in range(start, end)])
        return bars[end].volume / average_volume

    def calculate_variance(self, bars):
        closes = [bar.close for bar in bars]
        return np.var(closes)

    def calculate_quarter_profit_growth(self, income_statements, trade_date):
        for i in range(len(income_statements)-1, 0, -1):
            if income_statements[i].pub_date < trade_date:
                return income_statements[i].NETPROFIT / income_statements[i - 4].NETPROFIT - 1
        return 0

    def calculate_quarter_business_growth(self, income_statements, trade_date):
        for i in range(len(income_statements)-1, 0, -1):
            if income_statements[i].pub_date < trade_date:
                return income_statements[i].BIZINCO / income_statements[i - 4].BIZINCO - 1
        return 0

    def calculate_eps_growth(self, primary_finance_indicators, trade_date):
        for i in range(len(primary_finance_indicators)-1, 0, -1):
            if primary_finance_indicators[i].pub_date < trade_date:
                if i >= 4 and primary_finance_indicators[i - 4].EPSBASIC > 0:
                    return primary_finance_indicators[i].EPSBASIC / primary_finance_indicators[i - 4].EPSBASIC - 1
        return 0

    def calculate_increase_before_fallback(self, bars, pos):
        '''
        在i点之前已经从最低点上升的幅度，即此次调整前上升了多少,
        找最低点方法，最低点距离左侧高点跌了25%，右侧上升到i点
        :param bars:
        :param pos:
        :return:
        '''
        lowest_bar = None
        for i in range(pos-1, 0, -1):
            if bars[i].high > bars[pos].high:
                break
            if not lowest_bar or lowest_bar.high > bars[i].high:
                lowest_bar = bars[i]
            if (bars[i].high - lowest_bar.high) * 100 / bars[i].high > 25:
                break
        return (bars[pos].close - lowest_bar.close) / lowest_bar.close if lowest_bar else 0

    '''
    一年新高测试
    '''
    def strategy_test(self, code):
        bars = self.stockBarDao.getAll(code)
        derivatives = self.stockFundamentals.getAll(code, TradingDerivativeIndicator)

        n = len(bars)

        closes = np.array([bar.close for bar in bars])
        if np.isnan(np.mean(closes)):
            return (-1, -1)

        sma10 = talib.SMA(closes, 10)
        for i in range(n):
            bars[i].sma10 = sma10[i]

        sma20 = talib.SMA(closes, 20)
        for i in range(n):
            bars[i].sma20 = sma20[i]

        sma50 = talib.SMA(closes, 50)
        for i in range(n):
            bars[i].sma50 = sma50[i]

        sma120 = talib.SMA(closes, 120)
        for i in range(n):
            bars[i].sma120 = sma120[i]

        sma250 = talib.SMA(closes, 250)
        for i in range(n):
            bars[i].sma250 = sma250[i]


        win = 0
        total = 0
        win_ratio = []
        seen_dates = []

        buy_points = []
        for i in range(250, n):
            # i点没有一年新高，过滤掉
            for j in range(i-250, i):
                if bars[j].close > bars[i].close:
                    continue



            # 寻找右边突破K线的点
            max_decrease = 0
            for j in range(i + 1, n):
                max_decrease = max(max_decrease, bars[i].high - bars[j].low)
                if bars[j].high > bars[i].high:
                    # 调整幅度小于30
                    max_decrease_percent = max_decrease * 100.0 / bars[i].high

                    # 股价在所有均线之上
                    gt_MAs = bars[j].close > bars[j].sma10 and bars[j].close > bars[j].sma20 and \
                             bars[j].close > bars[j].sma50 and bars[j].close > bars[j].sma120 and \
                             bars[j].close > bars[j].sma250

                    # 调整周期长度小于250天
                    period_lt_250 = (j - i <= 250)

                    # 算PE，PB高度 < 70%
                    pe_height = self.calculate_pe_heigt_eight_year(bars[j].trade_date, derivatives)

                    # 平均换手率 < 3% (or avg)

                    # 调整期内的方差
                    var = self.calculate_variance(bars[i:j])

                    # 长期缓慢上涨股还是阴跌暴涨股，统计上涨时间/下跌时间

                    # 历史策略成功率

                    # 在i点之前已经上升的幅度，即此次调整前上升了多少

                    # j点的RPS强度

                    # j点的交易量/(i,j)的平均交易量

                    # 当期和上年度的净利润增速


                    if max_decrease_percent < 30 and \
                            gt_MAs and period_lt_250 and \
                            bars[j].sma120 > bars[j].sma250 * 0.96 and \
                            bars[j].sma50 > bars[j].sma120 * 0.99 and \
                            var <= 0.5 and \
                            bars[j].trade_date not in seen_dates and \
                            bars[j].trade_date > datetime(2016,1,1).date():

                        seen_dates.append(bars[j].trade_date)

                        # 计算止损线为7%，能获得的最大收益
                        max_price = 0
                        days_to_max_price = 0
                        max_price_date = ""
                        for k in range(j, n):
                            if bars[k].close < bars[j].close * 0.93:
                                break

                            days_to_max_price = k - j
                            if bars[k].close > max_price:
                                max_price = bars[k].close
                                max_price_date = bars[k].trade_date
                            # 考虑止盈策略时的收益
                            # if bars[k].close < max(max_price*0.9, bars[j].close*0.93):
                            #     if bars[k].close > bars[j].close * 1.2:
                            #         win+=1
                            #         print("win++")
                            #     max_price = bars[k].close
                            #     break
                            # end止盈策略
                        p = (max_price - bars[j].close) * 100.0 / bars[j].close
                        buy_points.append({
                            "code": code,
                            "start": bars[i],
                            "end": bars[j],
                            "gain": p,
                            "days": days_to_max_price,
                            "var": var,
                            "max_price_date": max_price_date
                        })
                    break

        # 删除相互包含的买点，保留第一个买点，即包含的
        for i in range(1, len(buy_points)):
            if buy_points[i]["end"].trade_date <= buy_points[i-1]["end"].trade_date:
                buy_points[i - 1]["remove"] = 1

        buy_points_cleaned = []
        for i in range(0, len(buy_points)):
            buy_point = buy_points[i]
            if "remove" not in buy_point:
                buy_points_cleaned.append(buy_point)

        buy_points = buy_points_cleaned

        # 删除max_price_date相等的买点，保留第一个买点
        for i in range(1, len(buy_points)):
            if buy_points[i]["max_price_date"] == buy_points[i-1]["max_price_date"]:
                buy_points[i]["remove"] = 1

        buy_points_cleaned = []
        for i in range(0, len(buy_points)):
            buy_point = buy_points[i]
            if "remove" not in buy_point:
                buy_points_cleaned.append(buy_point)

        buy_points = buy_points_cleaned

        for buy_point in buy_points:
            bar_start = buy_point["start"]
            bar_end = buy_point["end"]
            print(bar_start.code, bar_start.trade_date, bar_start.close, bar_end.trade_date, bar_end.close,
                  str(buy_point["gain"]) + "%", buy_point["days"], "d=", buy_point["max_price_date"])
            if buy_point["gain"] > 50:
                win+=1
                win_ratio.append(buy_point["gain"])
            total+=1
        print(code, "total = ", total, "win = ", win, "loss = ", total - win, "win_ratio", np.mean(win_ratio),
              win_ratio)
        return total, win


if __name__ == "__main__":
    analyzer = BuyPointInvestigation()
    stockDao = StockDao()
    stocks = stockDao.getStockList()

    # analyzer.strategy1('000001')
    # analyzer.strategy1('000739')
    # analyzer.strategy1('600149')
    #
    # analyzer.strategy1('600466')
    # analyzer.strategy1('601390')
    # analyzer.strategy1('600028')


    # random.shuffle(stocks)
    # total = 0
    # win = 0
    # n = 0
    # for code in stocks:
    #     (t,w) = analyzer.strategy1(code)
    #     if t == -1:
    #         continue
    #     total += t
    #     win += w
    #     n+=1
    #     if n > 50:
    #         break
    #
    # print(total, win)

