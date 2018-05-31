# coding: utf-8
from datetime import date

from models.models import IndexConstituent
from storage.IndexConstituentDao import IndexConstituentDao

import json

from storage.IndexWeightDao import IndexWeightDao


class IndexConstituentManager:
    def __init__(self):
        self.indexConstituentDao = IndexConstituentDao()
        self.indexWeightDao = IndexWeightDao()

    def getWeights(self, code, date):
        model = self.indexWeightDao.getConstituents(code, date)
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
    def _getConstituents(self, code, date):
        result = self.indexConstituentDao.getConstituents(code, date)
        if result is not None:
            return self.__formatConstituents(result)
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
    manager.getWeights('000001', date(2017, 1, 4))