# coding=utf-8
import json
from datetime import timedelta, datetime
import time

from common.Utils import Utils
from models.models import IndexConstituent
from spider.v3.GMBaseSpiderV3 import GMBaseSpiderV3
from storage.IndexConstituentDao import IndexConstituentDao
from storage.IndexesDao import IndexesDao


class IndexConstituentsSpider(GMBaseSpiderV3):

    def __init__(self):
        super(IndexConstituentsSpider, self).__init__()
        self.constituentsDao = IndexConstituentDao()
        self.indexesDao = IndexesDao()

    def rawDataToModel(self, code, constituent):
        model = self._rawDataToModel(code, constituent, IndexConstituent)
        model.constituents = json.dumps(model.constituents)
        model.code = code
        model.no_weight = 0
        return model

    def downloadConstituents(self, code):
        startDate = self.constituentsDao.getLatestDate(code) + timedelta(days=1)
        endDate = datetime.now() + timedelta(days=1)

        print("[Download Constituents] start=", startDate, "end=", endDate, "code=", self.getIndexSymbol(code) + "." + code)
        results = self.getHistoryConstituents(index=self.getIndexSymbol(code) + "." + code, start_date=startDate,
                                              end_date=endDate)

        constituents = []
        for item in results:
            if item['trade_date'].date() >= startDate:
                constituents.append(self.rawDataToModel(code, item))

        print("[Download Constituents] count = ", len(constituents), "\n")
        self.constituentsDao.addAll(constituents)
        return constituents

    def checkAndUpdateLatestConstituents(self, code):
        result = self.getConstituents(self.codeToIndexSymbol(code), "symbol, weight")
        dic = {}
        for item in result:
            dic[item["symbol"]] = item['weight']

        today = datetime.now().date()
        last = self.constituentsDao.getConstituents(code, today)
        print(code)
        if last is None:
            if len(dic) == 0:
                print("[%s] has no constituent found")
            else:
                print(code, last, dict)
        elif not Utils.isConstituentsEqual(dic, json.loads(last.constituents)):
            model = IndexConstituent()
            model.code = code
            model.constituents = json.dump(dic)
            model.trade_date = today
            model.no_weight = 0
            self.constituentsDao.add(model)
        else:
            print("[%s] constituent is up to date." % code)

    def downloadAllIndexConstituents(self):
        indexes = self.indexesDao.getIndexList()
        for code in indexes:
            self.downloadConstituents(code)
            time.sleep(0.1)

    def checkAndUpdateAllLatestConstituents(self):
        indexes = self.indexesDao.getIndexList()
        for code in indexes:
            self.checkAndUpdateLatestConstituents(code)
            time.sleep(0.1)

if __name__ == "__main__":
    spider = IndexConstituentsSpider()
    spider.downloadConstituents('000001')