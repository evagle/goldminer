# coding: utf-8

'''
十周线买卖规则

买入条件
自动化条件
1. 周k线上穿10周线，需满足前一周低于10周线，本周大于十周线
3. 十周线处于上涨趋势，至少上涨n（暂设n=1）周，n为1表示本周的10周线要比上周10周线高（此条可以继续优化，在明确的上涨趋势中可以忍受轻微的下降，
但是前期严格遵守，溺水三千只取一瓢）
4. 查看周线是否满足一些经典形态，例如口袋支点，w型底部，欧奈尔带柄茶杯形态，结构是否紧凑
5. close / 50周均线 >= 1.45, 满足这个条件的突破80%都失败了
6. 待研究：月线反转，rps50>90

人工过滤
2. 十周线上涨且处于第一个基底，最底部筑底阶段的底部回调风险较高，均线可能继续向下，过滤掉这种情况，暂时只能人工过滤，但是抽样来看，
这点非常重要，能过滤掉大部分在主跌过程中的假突破


卖出规则
1. 买入后设止损线-5%，跌破就卖
2. 盈利10%-20%，则提高止损线到+5%
3. 当盈利超过20%，则
    * 止损线提高到15%（or 10%，带测试）
    * 跌破10周线或者跌破下趋势线卖出
4. 如果前期已经突破下趋势线，现在突破10周线，则一定先卖出
5. 为了避免因为毛刺而贸然卖错，制定了一个“背离”验证规则。所谓的“背离”，是指当日收盘低于50日均线，并且接下来次日股价低于前日的最低价。这个背离可以辅助10周线进行判断卖出。
6. 如果是放量大跌>7%甚至跌停跌穿50日线，先走为妙，可以少赚，保住利润。
'''

import decimal
import math
import random
from datetime import datetime

import numpy as np
import pandas as pd
import talib
import tushare as ts

from goldminer.common.Utils import Utils
from goldminer.investigation.buy_signals.BuyPointBase import BuyPointBase
from goldminer.models.models import TradingDerivativeIndicator, IncomeStatement, PrimaryFinanceIndicator
from goldminer.storage.StockDao import StockDao


class MATenWeek(BuyPointBase):

    def find_high_low(self, bars, trade_date, n, stop_ratio):
        minimum = 1e6
        maximum = 0
        base = 0
        for i in range(len(bars)):
            if bars[i].trade_date == trade_date:
                base = bars[i].close
                for j in range(i+1, min(i+n+1, len(bars))):
                    if bars[j].close < minimum:
                        minimum = bars[j].close
                    if bars[j].close > maximum:
                        maximum = bars[j].close
                    # 到达止损线停止
                    if minimum/base < stop_ratio:
                        break

        return [minimum/base, maximum/base]

    # 一年新高图形
    def ma_ten_weeks_buy_points(self, code):
        bars = self.stockBarNoAdjustDao.getAll(code)
        # bars = Utils.pre_adjust(bars)

        # bars = self.tsStockBarSpider.getDailyBars(code, adj='qfq')

        # derivatives = self.stockFundamentals.getAll(code, TradingDerivativeIndicator)
        # primary_finance_indicators = self.stockFundamentals.getAll(code, PrimaryFinanceIndicator)
        income_statements = self.stockFundamentals.getAll(code, IncomeStatement)

        week_bars = Utils.dailyBar2WeeklyBar(code, bars)

        n = len(bars)
        if n == 0:
            return (-1, -1)

        self.calculate_ma(bars, [10, 20, 50, 120, 250])
        self.calculate_ma(week_bars, [5, 10, 20, 30, 50])

        self.calculate_amplitude(bars)
        self.calculate_amplitude(week_bars)


        buy_points = []
        a = 0
        b = 0
        for i in range(50, len(week_bars)):
            bar = week_bars[i]
            pre_bar = week_bars[i-1]

            '''
            1. 周k线上穿10周线，需满足前一周低于10周线，本周大于十周线
            2. 十周线处于上涨趋势，至少上涨n（暂设n=1）周，n为1表示本周的10周线要比上周10周线高
            3. close / 50周均线 >= 1.45, 满足这个条件的突破80%都失败了
            '''
            # 前30周到前5周的最低点10周线数值
            min_in_5_30 = 1e6
            for j in range(i-20, i-2):
                if min_in_5_30 > week_bars[j].sma10:
                    min_in_5_30 = week_bars[j].sma10

            # bar_rps = self.stockBarDao.getByCodeAndDate(code, bar.end_date)

            # bar.sma10 > 1.03 * min_in_5_30 and \
            #     (bar.close - pre_bar.close ) / pre_bar.close < 0.2 and \
            #     (pre_bar.close - week_bars[i-2].close) / week_bars[i-2].close > -0.1 \

            profit_growth = self.calculate_quarter_profit_growth(income_statements, bar.end_date) * 100

            if pre_bar.sma10 <= bar.sma10 and \
                bar.close > bar.sma10 and pre_bar.close < pre_bar.sma10 and \
                bar.close / bar.sma50 < 1.45 and \
                bar.rps50 > 85 and \
                profit_growth > 20 \
                :

                minimum, maximum = self.find_high_low(bars, bar.end_date, 120, 0.93)
                # 获取rps数据


                if maximum < 1.1:
                    print(code, bar.end_date, bar.close, [minimum, maximum], "*****")
                    target = 0
                else:
                    print(code, bar.end_date, bar.close, [minimum, maximum])
                    target = 1

                buy_point = {}
                buy_point['code'] = code
                buy_point['trade_date'] = bar.end_date
                buy_point['close_sma50'] = bar.close / bar.sma50
                buy_point['minimum_60d'] = minimum
                buy_point['maximum_60d'] = maximum
                buy_point['target'] = target

                buy_points.append(buy_point)

        return pd.DataFrame.from_records(buy_points)


if __name__ == "__main__":
    analyzer = MATenWeek()
    stockDao = StockDao()
    stocks = stockDao.getStockList()

    # analyzer.ma_ten_weeks_buy_points('000032')
    # exit(1)
    training_data = None
    num = len(stocks)
    for i in range(50):
        code = stocks[i]
        print("processing", i, code)
        try:
            df = analyzer.ma_ten_weeks_buy_points(code)
            if type(df) == tuple:
                print("Data error ", code)
                continue
        except Exception as e:
            print("Data error ", code, e)
            continue

        if training_data is None:
            training_data = df
        else:
            training_data = pd.concat([training_data, df])


    output_filename = "ma_ten_week_%d_%s.tsv" % (num, datetime.now().strftime("%Y-%m-%d"))
    training_data.to_csv(output_filename, sep="\t", index=False)

