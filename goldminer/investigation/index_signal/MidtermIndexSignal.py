# coding: utf-8

'''
发现指数中期信号
'''

import talib
import numpy as np

from goldminer.common.Utils import Utils
from goldminer.storage.IndexDailyBarDao import IndexDailyBarDao


class MidtermIndexSignal:
    def __init__(self):
        self.indexBarDao = IndexDailyBarDao()

    def find(self, code):
        daily_bars = self.indexBarDao.getByCode(code)
        weekly_bars = Utils.dailyBar2WeeklyBar(code, daily_bars)

        n = len(weekly_bars)

        closes = np.array([bar.close for bar in weekly_bars])
        if np.isnan(np.mean(closes)):
            return (-1, -1)

        sma10 = talib.SMA(closes, 9)
        for i in range(n):
            weekly_bars[i].sma10 = sma10[i]

        sma20 = talib.SMA(closes, 20)
        for i in range(n):
            weekly_bars[i].sma20 = sma20[i]

        result = {}
        for i in range(n):
            bar = weekly_bars[i]
            if bar.sma10 is None:
                continue

            if bar.close > bar.sma10:
                if hasattr(weekly_bars[i - 1], "close_gt_ma10") and weekly_bars[i - 1].close_gt_ma10 > 0:
                    bar.close_gt_ma10 = weekly_bars[i - 1].close_gt_ma10 + 1
                else:
                    bar.close_gt_ma10 = 1
            else:
                if hasattr(weekly_bars[i - 1], "close_gt_ma10") and weekly_bars[i - 1].close_gt_ma10 < 0:
                    bar.close_gt_ma10 = weekly_bars[i - 1].close_gt_ma10 - 1
                else:
                    bar.close_gt_ma10 = -1

            print(code, bar.end_date, bar.close_gt_ma10)
            result[bar.end_date] = bar.close_gt_ma10
        return result


if __name__ == "__main__":
    codes = ["000001",            # 上证指数
             "399001", "399106",  # 深证成指，深证综指
             "399006", "399102",  # 创业板指，创业板综
             "399005", "399101",  # 中小板指，中小板综
             "000016", "000300",  # 上证50, 沪深300
             "000905", "000852",  # 中证500，中证1000
             "399311",            # 国政1000
             "399678", "000011",  # 深次新股，
             "399108", "399318",  # 深证B指，国政B指
             "399003", "000003",  # 成份B指，B股指数
             ]
    indexSignal = MidtermIndexSignal()
    dates = indexSignal.find("000001").keys()

    tmp = {}
    for d in dates:
        tmp[d] = []
    for code in codes:
        result = indexSignal.find(code)
        for d in tmp:
            item = tmp[d]
            if d in result:
                item.append(result[d])
            else:
                item.append(0)

    previous = ""
    for d in tmp:
        positive_in_6 = 0
        for i in tmp[d][:6]:
            if i > 0:
                positive_in_6+=1
        positive_all = 0
        for i in tmp[d]:
            if i > 0:
                positive_all+=1

        if previous == "start" or previous == "continue":
            if positive_in_6 < 3 or positive_all < 9:
                print("E**", d, tmp[d], "\n")
                previous = ""
                continue

        if positive_in_6 >= 3 and positive_all >= 8:
            if previous != "start" and previous != "continue":
                print("S**", d, tmp[d])
                previous = "start"
            else:
                print("  C", d, tmp[d])
                previous = "continue"
        else:
            previous = ""