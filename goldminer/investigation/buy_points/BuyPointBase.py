# coding: utf-8
import math

import numpy as np
import talib

from goldminer.spider.tushare.TSStockBarSpider import TSStockBarSpider
from goldminer.storage.IndexPrimaryIndicatorDao import IndexPrimaryIndicatorDao
from goldminer.storage.StockDailyBarAdjustNoneDao import StockDailyBarAdjustNoneDao
from goldminer.storage.StockDailyBarAdjustPrevDao import StockDailyBarAdjustPrevDao
from goldminer.storage.StockFundamentalsDao import StockFundamentalsDao


class BuyPointBase:
    def __init__(self):
        self.stockBarAdjustPrevDao = StockDailyBarAdjustPrevDao()
        self.stockBarNoAdjustDao = StockDailyBarAdjustNoneDao()
        self.stockFundamentals = StockFundamentalsDao()
        self.indexIndicatorDao = IndexPrimaryIndicatorDao()
        self.tsStockBarSpider = TSStockBarSpider()

    def get_closes(self, bars):
        if len(bars) == 0:
            return None
        closes = np.array([bar.close for bar in bars])
        if np.isnan(np.mean(closes)):
            return None
        return closes

    def calculate_ma(self, bars, periods):
        closes = self.get_closes(bars)
        if closes is None:
            return False
        for period in periods:
            sma = talib.SMA(closes, period)
            for i in range(len(bars)):
                setattr(bars[i], "sma" + str(period), sma[i])
        return True

    def calculate_amplitude(self, bars):
        for bar in bars:
            bar.outer_amplitude = (bar.high - bar.low) / bar.low if bar.low > 0 else 0

        for bar in bars:
            bar.inner_amplitude = math.fabs(bar.close - bar.open) / bar.open if bar.open > 0 else 0

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
                n += 1
        return turn_rate / n if n > 0 else 0

    # 从上市日起比当前价格低的天数
    def calculate_days_with_lower_price(self, bars, pos):
        close = bars[pos].close
        days = 0
        for i in range(pos - 1, 0, -1):
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
        for i in range(pos - 1, 0, -1):
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
        for i in range(len(income_statements) - 1, 0, -1):
            if income_statements[i].pub_date < trade_date:
                return income_statements[i].NETPROFIT / income_statements[i - 4].NETPROFIT - 1
        return 0

    def calculate_quarter_business_growth(self, income_statements, trade_date):
        for i in range(len(income_statements) - 1, 0, -1):
            if income_statements[i].pub_date < trade_date:
                return income_statements[i].BIZINCO / income_statements[i - 4].BIZINCO - 1
        return 0

    def calculate_eps_growth(self, primary_finance_indicators, trade_date):
        for i in range(len(primary_finance_indicators) - 1, 0, -1):
            if primary_finance_indicators[i].pub_date < trade_date:
                if i >= 4 and primary_finance_indicators[i - 4].EPSBASIC > 0:
                    return primary_finance_indicators[i].EPSBASIC / primary_finance_indicators[i - 4].EPSBASIC - 1
        return 0

    def calculate_increase_before_fallback(self, bars, pos):
        '''
        在pos点之前已经从最低点上升的幅度，即此次调整前上升了多少,
        找最低点方法，最低点距离左侧高点跌了25%，右侧上升到i点
        :param bars:
        :param pos:
        :return:
        '''
        lowest_bar = None
        for i in range(pos - 1, 0, -1):
            if bars[i].high > bars[pos].high:
                break
            if not lowest_bar or lowest_bar.high > bars[i].high:
                lowest_bar = bars[i]
            if (bars[i].high - lowest_bar.high) * 100 / bars[i].high > 25:
                break
        return (bars[pos].close - lowest_bar.close) / lowest_bar.close if lowest_bar else 0

    def none_to_zero(self, x):
        return x if x is not None else 0