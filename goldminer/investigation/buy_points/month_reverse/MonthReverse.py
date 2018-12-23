# coding: utf-8

'''
{
月线反转3.0
  (1)日线收盘价站上年线；
  (2)一月内曾创50日新高；
  (3)RPS50大于85；
  (4)一个月内收盘价站上年线的天数大于3，小于30；
  (5)最高价距离120日内的最高价不到10%；
}

Z:=EXTDATA_USER(3,0);{50天的}

RPS50:=Z/10;

D:=IF(RPS50>=85,1,0);{RPS50大于85}

A:=C/MA(C,250)>1;{站上年线}

NH:=IF(H<HHV(H,50),0,1);

B:=COUNT(NH,30);{一月内曾创50日新高}

NN:=IF(C>MA(C,250),1,0);

AA:=COUNT(NN,30);

AB:=HIGH/HHV(HIGH,120)>0.9;{最高价距离120日内的最高价不到10%}

PF:=FINVALUE(184) > 20; {利润增速大于20%}

DRAWICON(BARSSINCEN((A AND B AND D AND  AA>3 AND AA<30 AND AB),30)=0,LOW,34);


'''
import decimal
import math
from datetime import datetime

import numpy as np
import pandas as pd
import talib

from goldminer.investigation.buy_points.BuyPointBase import BuyPointBase
from goldminer.models.models import TradingDerivativeIndicator, PrimaryFinanceIndicator, IncomeStatement
from goldminer.storage.StockDao import StockDao


class MonthReverse(BuyPointBase):

    # 一年新高图形
    def month_reverse_buy_points(self, code):
        bars = self.stockBarDao.getAll(code)
        derivatives = self.stockFundamentals.getAll(code, TradingDerivativeIndicator)
        primary_finance_indicators = self.stockFundamentals.getAll(code, PrimaryFinanceIndicator)
        income_statements = self.stockFundamentals.getAll(code, IncomeStatement)

        n = len(bars)
        if n == 0:
            return (-1, -1)

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
            if sma250[i] > 0:
                bars[i].close_sma250 = bars[i].close / sma250[i]
            else:
                bars[i].close_sma250 = 0

        for bar in bars:
            bar.outer_amplitude = (bar.high - bar.low) / bar.low if bar.low > 0 else 0

        for bar in bars:
            bar.inner_amplitude = math.fabs(bar.close - bar.open) / bar.open if bar.open > 0 else 0

        for i in range(120, n):
            is_new_high_50 = True
            for j in range(i - 50, i):
                if bars[j].close > bars[i].close:
                    is_new_high_50 = False
                    break
            if is_new_high_50:
                bars[i].new_high = 1

        last_point = 0
        buy_points = []
        # 当天创新高，而且最近一个月内没创过新高的
        for i in range(250, n):

            # 一个月内创过50新高
            new_high_50_counts = 0
            for j in range(i - 30, i + 1):
                if hasattr(bars[j], "new_high") and bars[j].new_high == 1:
                    new_high_50_counts += 1

            # 一个月内站上年线的天数
            days_above_sma250 = 0
            for j in range(i - 30, i + 1):
                if bars[j].close_sma250 > 1:
                    days_above_sma250 += 1

            # 当日最高价/120日内最高价
            high_120 = 0
            for j in range(i - 120, i + 1):
                high_120 = max(bars[j].high, high_120)

            high_devide_high_120 = bars[i].high / high_120 if high_120 > 0 else 0

            # 一年内最低点
            min_price = 1e8
            for j in range(i - 250, i):
                if bars[j].close > 0:
                    min_price = min(min_price, bars[j].close)

            # 一年内最低点到现在的涨幅
            max_increase = (bars[i].close - min_price) * 100.0 / min_price

            # 股价在所有均线之上
            gt_MAs = bars[i].close > bars[i].sma10 and bars[i].close > bars[i].sma20 and \
                     bars[i].close > bars[i].sma50 and bars[i].close > bars[i].sma120 and \
                     bars[i].close > bars[i].sma250

            # 算PE，PB高度
            pe_height = self.calculate_pe_heigt_eight_year(bars[i].trade_date, derivatives)
            pb_height = self.calculate_pb_heigt_eight_year(bars[i].trade_date, derivatives)

            # 一年平均换手率 < 3% (or avg)
            average_turn_rate = self.calculate_average_turn_rate(bars[i - 250].trade_date, bars[i].trade_date,
                                                                 derivatives)

            # 一年内方差
            variance = self.calculate_variance(bars[i - 250:i])

            # 到i日价格已经高于多少交易日
            days_with_lower_price = self.calculate_days_with_lower_price(bars, i)

            # 到i日已经几日新高
            new_high_days = self.calculate_new_high_days(bars, i)

            # 最低点算起到j日的天数
            days_from_bottom = self.calculate_days_from_bottom(bars, i)

            # 均线关系
            sma50_120 = bars[i].sma50 / bars[i].sma120
            sma120_250 = bars[i].sma120 / bars[i].sma250
            sma10_120 = bars[i].sma10 / bars[i].sma120
            sma10_250 = bars[i].sma10 / bars[i].sma250

            # close/sma250
            close_sma250 = bars[i].close / bars[i].sma250
            close_sma50 = bars[i].close / bars[i].sma50

            # 在i点之前已经上升的幅度，即此次调整前上升了多少,
            # 找最低点方法，最低点距离左侧跌了25%，右侧上升到i点
            increase_before_fallback = self.calculate_increase_before_fallback(bars, i)

            # i点的交易量/(i-30,i)的平均交易量
            volume_ratio = self.calculate_volume_ratio(bars, i - 30, i)

            # 同比净利润增速
            profit_growth = self.calculate_quarter_profit_growth(income_statements, bars[i].trade_date) * 100

            # 同比营收增速
            business_growth = self.calculate_quarter_business_growth(income_statements,
                                                                     bars[i].trade_date) * 100

            # 同比EPS增速
            eps_growth = self.calculate_eps_growth(primary_finance_indicators, bars[i].trade_date) * 100

            # i,j之间平均日内振幅，振幅=(high-low)/low
            average_outer_amplitude = np.mean([bar.outer_amplitude for bar in bars[i - 30:i]]) * 100

            # i,j之间平均日内波动，波动=abs(close-open)/open
            average_inner_amplitude = np.mean([bar.inner_amplitude for bar in bars[i - 30:i]]) * 100

            finance_indicator = self.get_primary_finance_indicator_by_date(bars[i].trade_date,
                                                                           primary_finance_indicators)
            if finance_indicator is not None:
                eps_basic = finance_indicator.EPSBASIC
                roe = finance_indicator.ROEWEIGHTED
            else:
                eps_basic = 0
                roe = 0

            rps50 = self.none_to_zero(bars[i].rps50)
            rps120 = self.none_to_zero(bars[i].rps120)
            rps250 = self.none_to_zero(bars[i].rps250)

            # 大盘点位高度，用上证综指000001
            indexIndicator = self.indexIndicatorDao.getByDate("000001", bars[i].trade_date)
            index_pe_height = indexIndicator.w_pe_height_ten_year
            index_pb_height = indexIndicator.w_pb_height_ten_year

            # TODO eps_rs, eps relative strength, 类似rps计算方式
            # eps_rs

            # print("**debug", code, bars[j].trade_date, pe_height, pb_height, average_turn_rate, variance, new_high_days, \
            #       sma50_120, sma120_250, sma10_20, sma10_250, volume_ratio, profit_growth)

            if (
                    rps50 > 85 and
                    close_sma250 > 1 and
                    new_high_50_counts > 0 and
                    3 < days_above_sma250 < 30 and
                    high_devide_high_120 > 0.9 and
                    i - last_point > 30
            ):
                last_point = i
                # 计算止损线为7%，能获得的最大收益
                max_price = 0
                for k in range(i, n):
                    if bars[k].close < bars[i].close * 0.9:
                        break

                    if bars[k].close > max_price:
                        max_price = bars[k].close

                gain = (max_price - bars[i].close) * 100.0 / bars[i].close
                target = (gain >= 50)

                derivative = self.get_derivatives_by_date(bars[i].trade_date, derivatives)

                buy_point = {}
                buy_point["code"] = code
                buy_point["start_date"] = bars[i].trade_date
                buy_point["max_increase"] = max_increase
                buy_point["pe_height"] = pe_height
                buy_point["pb_height"] = pb_height
                buy_point["average_turn_rate"] = average_turn_rate
                buy_point["variance"] = variance

                buy_point["average_outer_amplitude"] = average_outer_amplitude
                buy_point["average_inner_amplitude"] = average_inner_amplitude
                buy_point["volume_ratio"] = volume_ratio
                buy_point["profit_growth"] = profit_growth
                buy_point["business_growth"] = business_growth
                buy_point["eps_growth"] = eps_growth

                buy_point["increase_before_fallback"] = increase_before_fallback
                buy_point["pe"] = derivative.PETTM
                buy_point["pb"] = derivative.PB
                buy_point["mkt_cap"] = int(derivative.TOTMKTCAP / decimal.Decimal(1e8))
                buy_point["sma50_120"] = sma50_120
                buy_point["sma120_250"] = sma120_250
                buy_point["sma10_120"] = sma10_120
                buy_point["sma10_250"] = sma10_250
                buy_point["close_sma50"] = close_sma50
                buy_point["close_sma250"] = close_sma250

                buy_point["new_high_days"] = new_high_days
                buy_point["days_with_lower_price"] = days_with_lower_price
                buy_point["days_from_bottom"] = days_from_bottom

                buy_point["roe"] = roe
                buy_point["eps"] = eps_basic

                buy_point["rps50"] = rps50
                buy_point["rps120"] = rps120
                buy_point["rps250"] = rps250

                buy_point["index_pe_height"] = index_pe_height
                buy_point["index_pb_height"] = index_pb_height

                buy_point["new_high_50_counts"] = new_high_50_counts
                buy_point["days_above_sma250"] = days_above_sma250
                buy_point["high_devide_high_120"] = high_devide_high_120

                buy_point["gain"] = gain
                buy_point["target"] = 1 if target else 0
                buy_points.append(buy_point)
                print(buy_point)

        return pd.DataFrame.from_records(buy_points)


if __name__ == "__main__":
    analyzer = MonthReverse()
    stockDao = StockDao()
    stocks = stockDao.getStockList()

    df = analyzer.month_reverse_buy_points("300104")
    df.to_csv("~/buypoints.tsv", sep="\t", index=False)

    training_data = None
    num = len(stocks)
    for i in range(num):
        code = stocks[i]
        print("processing", i, code)
        try:
            df = analyzer.month_reverse_buy_points(code)
            if type(df) == tuple:
                print("Data error ", code)
                continue
        except Exception:
            print("Data error ", code)
            continue

        if training_data is None:
            training_data = df
        else:
            training_data = pd.concat([training_data, df])

    output_filename = "month_reverse_%d_%s.tsv" % (num, datetime.now().strftime("%Y-%m-%d"))
    training_data.to_csv(output_filename, sep="\t", index=False)
