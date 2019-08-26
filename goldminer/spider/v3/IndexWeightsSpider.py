# coding=utf-8
import json
import time
from datetime import timedelta, datetime

from goldminer.common.Utils import Utils
from goldminer.models.models import IndexWeight
from goldminer.spider.v3.GMBaseSpiderV3 import GMBaseSpiderV3
from goldminer.storage.IndexWeightDao import IndexWeightDao
from goldminer.storage.IndexesDao import IndexesDao


class IndexWeightsSpider(GMBaseSpiderV3):

    def __init__(self):
        super(IndexWeightsSpider, self).__init__()
        self.indexWeightDao = IndexWeightDao()
        self.indexesDao = IndexesDao()

    def rawDataToModel(self, constituent) -> IndexWeight:
        model = self._rawDataToModel(constituent, IndexWeight)
        model.constituents = json.dumps(model.constituents)
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
                models.append(self.rawDataToModel(item))

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