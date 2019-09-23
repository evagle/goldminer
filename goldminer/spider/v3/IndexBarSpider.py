# coding=utf-8
import time
from datetime import timedelta, datetime, date

from goldminer.common.logger import get_logger
from goldminer.indicators.StockManager import StockManager
from goldminer.models.models import IndexDailyBar
from goldminer.spider.v3.GMBaseSpiderV3 import GMBaseSpiderV3
from goldminer.storage.IndexDailyBarDao import IndexDailyBarDao
from goldminer.storage.IndexesDao import IndexesDao

logger = get_logger(__name__)


class IndexBarSpider(GMBaseSpiderV3):

    def __init__(self):
        super(IndexBarSpider, self).__init__()
        self.indexBarDao = IndexDailyBarDao()
        self.indexesDao = IndexesDao()

    def rawDataToModel(self, code, rawBar):
        model = self._rawDataToModel(rawBar, IndexDailyBar)
        model.code = code
        model.trade_date = rawBar['eob'].date()
        for key in ['pre_close', 'amount', 'open', 'close', 'high', 'low']:
            if getattr(model, key) is None:
                setattr(model, key, 0)
        return model

    def downloadBars(self, code):
        startDate = self.indexBarDao.getLatestDate(code) + timedelta(days=1)
        endDate = datetime.now() + timedelta(days=1)
        return self.downloadBarsByDateRange(code, startDate, endDate.date())

    def downloadBarsByDateRange(self, code, startDate: date, endDate: date, save=True):

        if startDate > datetime.now().date():
            logger.info("[%s] is up to date" % code)
            return None

        symbol = self.getIndexSymbol(code) + "." + code
        logger.info("[Download Index Bars] start=", startDate, "end=", endDate, "code=", symbol)
        bars = self.getHistory(symbol, "1d", startDate, endDate)
        bars = [self.rawDataToModel(code, bar) for bar in bars]
        if save:
            self.indexBarDao.addAll(bars)
            logger.info("[Download Index Bars] count=", len(bars), "\n")
        return bars

    def downloadAllIndexBars(self):
        indexes = self.indexesDao.getIndexList()
        for i in indexes:
            if self.downloadBars(i) is not None:
                time.sleep(0.1)

    '''
    检查每个index，如果有漏掉的bar就重新补齐
    '''
    def checkAllIndexBars(self):
        stockManager = StockManager()
        tradeDates = stockManager.getTradeDates()

        indexes = self.indexesDao.getIndexList()
        for code in indexes:
            pubDate = self.indexesDao.getIndexPublishDate(code)
            for d in tradeDates:
                if d < pubDate:
                    continue
                bar = self.indexBarDao.getByDate(code, d)
                if bar is None:
                    self.downloadBarsByDateRange(code, d, d)

if __name__ == "__main__":
    spider = IndexBarSpider()
    # spider.downloadBars('000001')
    spider.checkAllIndexBars()