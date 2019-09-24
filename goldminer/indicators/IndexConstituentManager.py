# coding: utf-8
import json
from datetime import date

from goldminer.models.models import IndexConstituent
from goldminer.storage.IndexWeightDao import IndexWeightDao
from goldminer.storage.IndexConstituentDao import IndexConstituentDao


class IndexConstituentManager:
    def __init__(self):
        self.indexConstituentDao = IndexConstituentDao()
        self.indexWeightDao = IndexWeightDao()
        self.__updateDates = None
        self.__lastQueryIndexCode = None
        self.__lastConstituents = None
        self.__lastQueryDate = None

    def getWeights(self, code, date):
        model = self.indexWeightDao.getByDate(code, date)
        if model is None:
            return None

        data = json.loads(model.constituents)
        weights = {}
        for k in data:
            weights[k[5:]] = data[k]
        print(weights)
        return weights

    def __formatConstituents(self, model: IndexConstituent):
        constituents = json.loads(model.constituents)
        return [model.code, model.trade_date, constituents]

    # 获取指数成份股，如果能获取到weights则直接返回
    # 否则尝试获取constituents
    # trade_date >= query_date && trade_date 最小
    def _getConstituents(self, code, d: date):
        # 如果查找的是上次查找的index code，并且日期并没有到达下一个constituent的日期，那就直接返回上一个
        if code == self.__lastQueryIndexCode:
            canUseCache = True
            for idate in self.__updateDates:
                if idate[0] == d and idate[0] != self.__lastQueryDate:
                    canUseCache = False
            if canUseCache:
                return self.__lastConstituents

        result = self.indexConstituentDao.getConstituents(code, d)
        if result is not None:
            constituents = self.__formatConstituents(result)
            self.__lastQueryDate = d
            self.__lastConstituents = constituents
            self.__updateDates = self.indexConstituentDao.getConstituentUpdateDates(code)
            self.__lastQueryIndexCode = code
            return constituents
        return None

    def _getConstituentsForTest(self, code, date):
        result = self._getConstituents(code, date)
        if result is None:
            return None
        return result[1]

    def getConstituents(self, code, date):
        result = self._getConstituents(code, date)
        if result is None:
            return None
        if isinstance(result[2], list):
            return result[2]
        data = json.loads(result[2])
        constituents = []
        for c in data:
            constituents.append(c[5:])
        return constituents

if __name__ == "__main__":
    manager = IndexConstituentManager()