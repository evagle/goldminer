# coding=utf-8
import json
from datetime import timedelta, datetime
import time

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

    def downloadAllIndexConstituents(self):
        indexes = self.indexesDao.getIndexList()
        for i in indexes:
            self.downloadConstituents(i)
            time.sleep(0.1)



if __name__ == "__main__":
    spider = IndexConstituentsSpider()
    spider.downloadConstituents('000001')