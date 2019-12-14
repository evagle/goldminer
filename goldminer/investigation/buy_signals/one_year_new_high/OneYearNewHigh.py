# coding: utf-8
import decimal
import math
from datetime import datetime

import numpy as np
import pandas as pd
import talib

from goldminer.investigation.buy_signals.BuyPointBase import BuyPointBase
from goldminer.models.models import TradingDerivativeIndicator, IncomeStatement, PrimaryFinanceIndicator
from goldminer.storage.StockDao import StockDao


class OneYearNewHigh(BuyPointBase):

    def has_break_through_gap(self, pos, bars):
        '''
        检查30日内是否有向上跳空缺口
        :param pos:
        :param bars:
        :return:
        '''
        for i in range(pos - 30, pos):
            if bars[i].low > bars[i - 1].high:
                return 1
        return 0

    # 一年新高图形
    def one_year_new_high_buy_points(self, code):
        bars = self.stockBarNoAdjustDao.getByCode(code)
        derivatives = self.stockFundamentals.getByCode(code, TradingDerivativeIndicator)
        primary_finance_indicators = self.stockFundamentals.getByCode(code, PrimaryFinanceIndicator)
        income_statements = self.stockFundamentals.getByCode(code, IncomeStatement)

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

        for bar in bars:
            bar.outer_amplitude = (bar.high - bar.low) / bar.low if bar.low > 0 else 0

        for bar in bars:
            bar.inner_amplitude = math.fabs(bar.close - bar.open) / bar.open if bar.open > 0 else 0

        last_new_high = 0
        for i in range(250, n):
            is_one_year_high = True
            for j in range(i - 250, i):
                if bars[j].close > bars[i].close:
                    is_one_year_high = False
                    break
            if is_one_year_high:
                bars[i].new_high = 1
                bars[i].days_since_last = i - last_new_high
                last_new_high = i

        buy_points = []
        # 当天创新高，而且最近一个月内没创过新高的
        for i in range(250, n):
            if not hasattr(bars[i], "new_high") or bars[i].new_high != 1 or bars[i].days_since_last <= 30:
                continue

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
            eps_basic = finance_indicator.EPSBASIC

            roe = finance_indicator.ROEWEIGHTED

            has_break_through_gap = self.has_break_through_gap(i, bars)

            rps50 = bars[i].rps50
            rps120 = bars[i].rps120
            rps250 = bars[i].rps250

            # 大盘点位高度，用上证综指000001
            indexIndicator = self.indexIndicatorDao.getByDate("000001", bars[j].trade_date)
            index_pe_height = indexIndicator.w_pe_height_ten_year
            index_pb_height = indexIndicator.w_pb_height_ten_year

            # TODO eps_rs, eps relative strength, 类似rps计算方式
            # eps_rs

            # print("**debug", code, bars[j].trade_date, pe_height, pb_height, average_turn_rate, variance, new_high_days, \
            #       sma50_120, sma120_250, sma10_20, sma10_250, volume_ratio, profit_growth)

            if gt_MAs:

                # 计算止损线为7%，能获得的最大收益
                max_price = 0
                for k in range(i, n):
                    if bars[k].close < bars[i].close * 0.93:
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

                buy_point["has_break_through_gap"] = has_break_through_gap

                buy_point["index_pe_height"] = index_pe_height
                buy_point["index_pb_height"] = index_pb_height

                buy_point["gain"] = gain
                buy_point["target"] = 1 if target else 0
                buy_points.append(buy_point)

        return pd.DataFrame.from_records(buy_points)


if __name__ == "__main__":
    analyzer = OneYearNewHigh()
    stockDao = StockDao()
    stocks = stockDao.getStockList()

    training_data = None
    num = len(stocks)
    for i in range(num):
        code = stocks[i]
        print("processing", i, code)
        try:
            df = analyzer.one_year_new_high_buy_points(code)
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

    output_filename = "one_year_new_high_%d_%s.tsv" % (num, datetime.now().strftime("%Y-%m-%d"))
    training_data.to_csv(output_filename, sep="\t", index=False)
