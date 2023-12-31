# coding: utf-8
import decimal
import math
import random
from datetime import datetime

import numpy as np
import pandas as pd

from goldminer.common.Utils import Utils
from goldminer.investigation.buy_signals.BuyPointBase import BuyPointBase
from goldminer.models.models import TradingDerivativeIndicator, IncomeStatement, PrimaryFinanceIndicator
from goldminer.storage.StockDao import StockDao


class FallbackNewHigh(BuyPointBase):

    # 策略1 上涨后长期整理，然后突破形态
    def fallback_new_high_buy_points(self, code):
        bars = self.stockBarDao.getByCode(code)
        derivatives = self.stockFundamentals.getByCode(code, TradingDerivativeIndicator)
        primary_finance_indicators = self.stockFundamentals.getByCode(code, PrimaryFinanceIndicator)
        income_statements = self.stockFundamentals.getByCode(code, IncomeStatement)

        n = len(bars)
        if n == 0:
            return (-1, -1)

        closes = np.array([bar.close for bar in bars])
        if np.isnan(np.mean(closes)):
            return (-1, -1)

        sma10 = Utils.SMA(closes, 10)
        for i in range(n):
            bars[i].sma10 = sma10[i]

        sma20 = Utils.SMA(closes, 20)
        for i in range(n):
            bars[i].sma20 = sma20[i]

        sma50 = Utils.SMA(closes, 50)
        for i in range(n):
            bars[i].sma50 = sma50[i]

        sma120 = Utils.SMA(closes, 120)
        for i in range(n):
            bars[i].sma120 = sma120[i]

        sma250 = Utils.SMA(closes, 250)
        for i in range(n):
            bars[i].sma250 = sma250[i]

        for bar in bars:
            bar.outer_amplitude = (bar.high - bar.low) / bar.low if bar.low > 0 else 0

        for bar in bars:
            bar.inner_amplitude = math.fabs(bar.close - bar.open) / bar.open if bar.open > 0 else 0

        # 记录之前出现过的买点，不重复计算
        win = 0
        total = 0
        win_ratio = []
        seen_dates = []

        buy_points = []
        for i in range(250, n):
            # 左边7个K线小于当前点，右边15个K线小于当前点
            left = right = True
            for j in range(i - 7, i):
                if bars[j].high > bars[i].high:
                    left = False
            for j in range(i + 1, min(i + 15, n)):
                if bars[j].high > bars[i].high:
                    left = False
            if not left or not right:
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
                    adjust_period = j - i
                    period_lt_250 = (adjust_period <= 250)

                    # 算PE，PB高度
                    pe_height = self.calculate_pe_heigt_eight_year(bars[j].trade_date, derivatives)
                    pb_height = self.calculate_pb_heigt_eight_year(bars[j].trade_date, derivatives)

                    # 平均换手率 < 3% (or avg)
                    average_turn_rate = self.calculate_average_turn_rate(bars[i].trade_date, bars[j].trade_date,
                                                                         derivatives)

                    # 调整期内的方差
                    variance = self.calculate_variance(bars[i:j])

                    # 到j日已经几日新高
                    days_with_lower_price = self.calculate_days_with_lower_price(bars, j)

                    # 到j日已经几日新高
                    new_high_days = self.calculate_new_high_days(bars, j)

                    # 最低点算起到j日的天数
                    days_from_bottom = self.calculate_days_from_bottom(bars, j)

                    # 均线关系
                    sma50_120 = bars[j].sma50 / bars[j].sma120
                    sma120_250 = bars[j].sma120 / bars[j].sma250
                    sma10_120 = bars[j].sma10 / bars[j].sma120
                    sma10_250 = bars[j].sma10 / bars[j].sma250

                    # close/sma250
                    close_sma250 = bars[j].close / bars[j].sma250
                    close_sma50 = bars[j].close / bars[j].sma50

                    # 长期缓慢上涨股还是阴跌暴涨股，统计上涨时间/下跌时间

                    # 历史策略成功率

                    # 在i点之前已经上升的幅度，即此次调整前上升了多少,
                    # 找最低点方法，最低点距离左侧跌了25%，右侧上升到i点
                    increase_before_fallback = self.calculate_increase_before_fallback(bars, i)

                    # j点的RPS强度

                    # j点的交易量/(i,j)的平均交易量
                    volume_ratio = self.calculate_volume_ratio(bars, i, j)

                    # 同比净利润增速
                    profit_growth = self.calculate_quarter_profit_growth(income_statements, bars[j].trade_date) * 100

                    # 同比营收增速
                    business_growth = self.calculate_quarter_business_growth(income_statements,
                                                                             bars[j].trade_date) * 100

                    # 同比EPS增速
                    eps_growth = self.calculate_eps_growth(primary_finance_indicators, bars[j].trade_date) * 100

                    # i,j之间平均日内振幅，振幅=(high-low)/low
                    average_outer_amplitude = np.mean([bar.outer_amplitude for bar in bars[i:j]]) * 100

                    # i,j之间平均日内波动，波动=abs(close-open)/open
                    average_inner_amplitude = np.mean([bar.inner_amplitude for bar in bars[i:j]]) * 100

                    # 10日日内振幅用来作为卖出指标判断

                    finance_indicator = self.get_primary_finance_indicator_by_date(bars[j].trade_date,
                                                                                   primary_finance_indicators)
                    eps_basic = finance_indicator.EPSBASIC

                    roe = finance_indicator.ROEWEIGHTED

                    rps50 = bars[j].rps50
                    rps120 = bars[j].rps120
                    rps250 = bars[j].rps250

                    # 大盘点位高度，用上证综指000001
                    indexIndicator = self.indexIndicatorDao.getByDate("000001", bars[j].trade_date)
                    index_pe_height = indexIndicator.w_pe_height_ten_year
                    index_pb_height = indexIndicator.w_pb_height_ten_year

                    # TODO eps_rs, eps relative strength, 类似rps计算方式
                    # eps_rs

                    # print("**debug", code, bars[j].trade_date, pe_height, pb_height, average_turn_rate, variance, new_high_days, \
                    #       sma50_120, sma120_250, sma10_20, sma10_250, volume_ratio, profit_growth)

                    if max_decrease_percent < 30 and \
                            gt_MAs and \
                            bars[j].trade_date not in seen_dates:

                        seen_dates.append(bars[j].trade_date)
                        # 计算止损线为7%，能获得的最大收益
                        max_price = 0
                        days_to_max_price = 0
                        max_price_date = ""
                        for k in range(j, n):
                            if bars[k].close < bars[j].close * 0.93:
                                break

                            if bars[k].close > max_price:
                                max_price = bars[k].close
                                max_price_date = bars[k].trade_date
                                days_to_max_price = k - j

                        gain = (max_price - bars[j].close) * 100.0 / bars[j].close
                        target = (gain >= 50)

                        derivative = self.get_derivatives_by_date(bars[j].trade_date, derivatives)

                        buy_point = {}
                        buy_point["code"] = code
                        buy_point["start_date"] = bars[i].trade_date
                        buy_point["end_date"] = bars[j].trade_date
                        buy_point["max_decrease"] = max_decrease_percent
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
                        buy_point["adjust_period"] = adjust_period
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

                        buy_point["gain"] = gain
                        buy_point["target"] = 1 if target else 0
                        buy_points.append(buy_point)
                    break

        return pd.DataFrame.from_records(buy_points)


if __name__ == "__main__":
    analyzer = FallbackNewHigh()
    stockDao = StockDao()
    stocks = stockDao.getStockList()

    df = analyzer.fallback_new_high_buy_points("000860")
    df.to_csv("~/buypoints.tsv", sep="\t", index=False)

    random.shuffle(stocks)
    training_data = None
    num = len(stocks)
    for i in range(num):
        code = stocks[i]
        print("processing", i, code)
        try:
            df = analyzer.fallback_new_high_buy_points(code)
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

    output_filename = "fallback_new_high_%d_%s.tsv" % (num, datetime.now().strftime("%Y-%m-%d"))
    training_data.to_csv(output_filename, sep="\t", index=False)
