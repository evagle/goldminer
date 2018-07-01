# coding: utf-8
import math
from decimal import Decimal
import numpy as np

from common import GMConsts


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
        m = int(math.floor((n-1)/2))
        if lst is None or n == 0:
            return None
        elif n % 2 == 1:
            return lst[m]
        else:
            return (lst[m] + lst[m+1])/2

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
        return [i for i in sourceList if lowerBound <=i <= upperBound]


if __name__ == "__main__":
    lst = []
    print(Utils.getMedian(lst))

    lst = [1]
    print(Utils.getMedian(lst))

    lst = [1,2]
    print(Utils.getMedian(lst))

    lst = [1,2,3]
    print(Utils.getMedian(lst))

    lst = [1,2,3,4]
    print(Utils.getMedian(lst))

