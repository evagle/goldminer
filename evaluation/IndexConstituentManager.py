# coding: utf-8
from datetime import date

from storage.IndexConstituentDao import IndexConstituentDao

import json


class IndexConstituentManager:
    def __init__(self):
        self.indexConstituentDao = IndexConstituentDao()

    def getWeights(self, code, date):
        result = self.indexConstituentDao.getConstituents(code, date)
        if result is None:
            return None

        data = json.loads(result[2])
        weights = {}
        for k in data:
            weights[k[5:]] = data[k]
        print(weights)
        return weights

    def __formatConstituents(self, data):
        if data[3] == 1:
            constituents = [c[5:] for c in json.loads(data[2])]
            return [data[0], data[1], constituents]
        else:
            keys = list(json.loads(data[2]).keys())
            constituents = [c[5:] for c in keys]
            return [data[0], data[1], constituents]

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
