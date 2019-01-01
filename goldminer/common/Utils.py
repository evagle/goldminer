# coding: utf-8
import datetime
import math
from decimal import Decimal

import numpy as np

from goldminer.common import GMConsts
from goldminer.models.IndexWeeklyBar import IndexWeeklyBar


class Utils:
    @staticmethod
    def getPropertiesOfClazz(clazz):
        properties = []
        for i in dir(clazz):
            if i[0:1] != "_":
                properties.append(i)
        return properties

    @staticmethod
    def isDictEqual(dictA: dict, dictB: dict):
        if dictA.keys() != dictB.keys():
            return False
        else:
            for k in dictA.keys():
                if math.fabs(dictA[k] - dictB[k]) > 1e6:
                    return False
        return True

    @staticmethod
    def isListEqual(listA: list, listB: list):
        if len(listA) != len(listB):
            return False
        else:
            for k in listA:
                if k not in listB:
                    return False
        return True

    @staticmethod
    def getMedian(lst: list):
        n = len(lst)
        m = int(math.floor((n - 1) / 2))
        if lst is None or n == 0:
            return None
        elif n % 2 == 1:
            return lst[m]
        else:
            return (lst[m] + lst[m + 1]) / 2

    @staticmethod
    def formatFloat(value: float, precision: int):
        format = "0."
        for i in range(precision):
            format += "0"
        return float(Decimal(value).quantize(Decimal(format)))

    # 四分法 interquartile range (IQR)
    # https://en.wikipedia.org/wiki/Interquartile_range#Examples
    @staticmethod
    def iqrFilter(sourceList):
        q25 = np.percentile(sourceList, 25)
        q75 = np.percentile(sourceList, 75)
        iqr = q75 - q25
        lowerBound = q25 - GMConsts.IQR_FACTOR * iqr
        upperBound = q75 + GMConsts.IQR_FACTOR * iqr
        return [i for i in sourceList if lowerBound <= i <= upperBound]

    @staticmethod
    def date2Week(date):
        week = date.isocalendar()
        return "%d_%d" % (week[0], week[1])

    @staticmethod
    def dailyBar2WeeklyBar(code, dailyBars):
        barsGroupByWeek = {}
        for bar in dailyBars:
            week = Utils.date2Week(bar.trade_date)

            if week in barsGroupByWeek:
                barsGroupByWeek[week].append(bar)
            else:
                barsGroupByWeek[week] = [bar]


        weeklyBars = []
        for week in barsGroupByWeek:
            bar = IndexWeeklyBar()

            bars = barsGroupByWeek[week]

            bar.code = code
            bar.start_date = bars[0].trade_date
            bar.end_date = bars[-1].trade_date
            bar.open = bars[0].open
            bar.close = bars[-1].close
            bar.high = max([b.high for b in bars])
            bar.low = min([b.low for b in bars])
            bar.amount = sum([b.amount for b in bars])
            bar.volume = sum([b.volume for b in bars])

            weeklyBars.append(bar)

        return weeklyBars

    @staticmethod
    def pre_adjust(bars):
        factor = bars[-1].adj_factor
        for bar in bars:
            bar.high = float(Decimal(bar.high) * bar.adj_factor / factor)
            bar.low = float(Decimal(bar.low) * bar.adj_factor / factor)
            bar.close = float(Decimal(bar.close) * bar.adj_factor / factor)
            bar.open = float(Decimal(bar.open) * bar.adj_factor / factor)
            bar.pre_close = float(Decimal(bar.pre_close) * bar.adj_factor / factor)

        return bars


if __name__ == "__main__":
    lst = []
    print(Utils.getMedian(lst))

    lst = [1]
    print(Utils.getMedian(lst))

    lst = [1, 2]
    print(Utils.getMedian(lst))

    lst = [1, 2, 3]
    print(Utils.getMedian(lst))

    lst = [1, 2, 3, 4]
    print(Utils.getMedian(lst))

