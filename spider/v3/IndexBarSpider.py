# coding=utf-8
import time
from datetime import timedelta, datetime

from models.models import IndexConstituent, IndexDailyBar
from spider.v3.GMBaseSpiderV3 import GMBaseSpiderV3
from storage.IndexDailyBarDao import IndexDailyBarDao
from storage.IndexesDao import IndexesDao


class IndexBarSpider(GMBaseSpiderV3):

    def __init__(self):
        super(IndexBarSpider, self).__init__()
        self.indexBarDao = IndexDailyBarDao()
        self.indexesDao = IndexesDao()

    def rawDataToModel(self, code, rawBar):
        model = self._rawDataToModel(code, rawBar, IndexDailyBar)
        model.code = code
        model.trade_date = rawBar['eob'].date()
        for key in ['pre_close', 'amount', 'open', 'close', 'high', 'low']:
            if getattr(model, key) is None:
                setattr(model, key, 0)
        return model

    def downloadBars(self, code):
        startDate = self.indexBarDao.getLatestDate(code) + timedelta(days=1)
        endDate = datetime.now() + timedelta(days=1)

        symbol = self.getIndexSymbol(code) + "." + code
        print("[Download Index Bars] start=", startDate, "end=", endDate, "code=", symbol)
        bars = self.getHistory(symbol, "1d", startDate, endDate)
        bars = [self.rawDataToModel(code, bar) for bar in bars]
        self.indexBarDao.addAll(bars)
        print("[Download Index Bars] count=", len(bars), "\n")
        return bars

    def downloadAllIndexBars(self):
        indexes = self.indexesDao.getIndexList()
        for i in indexes:
            self.downloadBars(i)
            time.sleep(0.1)


if __name__ == "__main__":
    spider = IndexBarSpider()
    spider.downloadBars('000001')
