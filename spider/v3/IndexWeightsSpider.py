# coding=utf-8
import json
from datetime import timedelta, datetime
import time

from common.Utils import Utils
from models.models import IndexConstituent, IndexWeight
from spider.v3.GMBaseSpiderV3 import GMBaseSpiderV3
from storage.IndexConstituentDao import IndexConstituentDao
from storage.IndexWeightDao import IndexWeightDao
from storage.IndexesDao import IndexesDao


class IndexWeightsSpider(GMBaseSpiderV3):

    def __init__(self):
        super(IndexWeightsSpider, self).__init__()
        self.indexWeightDao = IndexWeightDao()
        self.indexesDao = IndexesDao()

    def rawDataToModel(self, code, constituent) -> IndexWeight:
        model = self._rawDataToModel(code, constituent, IndexWeight)
        model.constituents = json.dumps(model.constituents)
        model.code = code
        return model

    def downloadConstituents(self, code):
        startDate = self.indexWeightDao.getLatestDate(code) + timedelta(days=1)
        endDate = datetime.now() + timedelta(days=1)

        print("[Download weights ] start=", startDate, "end=", endDate, "code=", self.getIndexSymbol(code) + "." + code)
        results = self.getHistoryConstituents(index=self.getIndexSymbol(code) + "." + code, start_date=startDate,
                                              end_date=endDate)

        models = []
        for item in results:
            if item['trade_date'].date() >= startDate:
                models.append(self.rawDataToModel(code, item))

        print("[Download weights ] count = ", len(models), "\n")
        self.indexWeightDao.addAll(models)
        return models

    def checkAndUpdateLatestConstituents(self, code):
        result = self.getConstituents(self.codeToIndexSymbol(code), "symbol, weight")
        dic = {}
        for item in result:
            dic[item["symbol"]] = item['weight']

        today = datetime.now().date()
        last = self.indexWeightDao.getByDate(code, today)
        if last is None:
            if len(dic) == 0:
                print("[%s] has no index weight found")
            else:
                print(code, last, dict)
        elif not Utils.isDictEqual(dic, json.loads(last.constituents)):
            model = IndexWeight()
            model.code = code
            model.constituents = json.dumps(dic)
            model.trade_date = today
            self.indexWeightDao.add(model)
            print("[%s] new index weight record" % code)
        else:
            print("[%s] index weight is up to date." % code)

    def downloadAllIndexConstituents(self):
        if datetime.now().day < 25:
            print("NO UPDATE: Index Weights from gm are published at the end of each month")
            return
        indexes = self.indexesDao.getIndexList()
        for code in indexes:
            self.downloadConstituents(code)
            time.sleep(0.1)

if __name__ == "__main__":
    spider = IndexWeightsSpider()
    spider.downloadConstituents('000001')