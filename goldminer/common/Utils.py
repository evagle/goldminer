# coding: utf-8
import math
from datetime import datetime
from decimal import Decimal

import numpy as np
import pandas as pd
import xlrd

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
            for rps in ["rps50", "rps120", "rps250"]:
                if hasattr(bars[-1], rps):
                    val = getattr(bars[-1], rps)
                    setattr(bar, rps, val)

            weeklyBars.append(bar)

        return weeklyBars

    @staticmethod
    def sma(bars, periods, field='close'):
        if len(bars) == 0 or len(periods) == 0:
            return None

        values = np.array([float(getattr(bar, field)) for bar in bars])
        if np.isnan(np.mean(values)):
            return None

        for n in periods:
            if field == 'close':
                attr = 'sma' + str(n)
            else:
                attr = 'sma_{}{}'.format(field, str(n))
            sma_n = Utils.SMA(values, n)

            for i in range(len(values)):
                setattr(bars[i], attr, sma_n[i])

        return bars

    @staticmethod
    def maxDate(date1, date2):
        return date1 if date1 > date2 else date2

    @staticmethod
    def minDate(date1, date2):
        return date1 if date1 < date2 else date2

    @staticmethod
    def parseConstituentUpdateDate(datestr):
        if type(datestr) == float:
            tuple = xlrd.xldate_as_tuple(datestr, 0)
            return datetime(tuple[0], tuple[1], tuple[2]).date()

        datestr = datestr.strip()
        if len(datestr) == 8 and datestr.find("-") < 0:
            format = "%Y%m%d"
        elif datestr.find("-") >= 0:
            parts = datestr.split("-")
            if len(parts) != 3:
                return None
            if len(parts[0]) != 4:
                return None
            format = "%Y-%m-%d"
        elif datestr.find("/") >= 0:
            parts = datestr.split("/")
            if len(parts) != 3:
                return None
            if len(parts[2]) != 4:
                return None
            format = "%m/%d/%Y"
        return datetime.strptime(datestr, format).date()

    @staticmethod
    def SMA(array, window):
        return pd.DataFrame(array).rolling(window=window).mean()[0].values.tolist()


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
