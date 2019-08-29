# coding=utf-8
import time
from datetime import timedelta, datetime

from goldminer.models.models import StockDailyBarAdjustNone
from goldminer.spider.v3.GMBaseSpiderV3 import GMBaseSpiderV3
from goldminer.storage.StockDailyBarAdjustNoneDao import StockDailyBarAdjustNoneDao
from goldminer.storage.StockDao import StockDao


class StockDailyBarAdjustNoneSpider(GMBaseSpiderV3):

    def __init__(self):
        super(StockDailyBarAdjustNoneSpider, self).__init__()
        self.stockBarDao = StockDailyBarAdjustNoneDao()
        self.stockDao = StockDao()

    def rawDataToModel(self, code, rawBar):
        model = self._rawDataToModel(rawBar, StockDailyBarAdjustNone)
        model.trade_date = rawBar['eob'].date()
        model.code = code
        for key in ['pre_close', 'amount', 'open', 'close', 'high', 'low']:
            if getattr(model, key) is None:
                setattr(model, key, 0)
        return model

    def downloadBars(self, code):
        startDate = self.stockBarDao.getLatestDate(code) + timedelta(days=1)
        endDate = datetime.now() + timedelta(days=1)

        return self.downloadBarsByDateRange(code, startDate, endDate)

    def downloadBarsByDateRange(self, code, startDate, endDate):
        if startDate >= datetime.now().date():
            print("[%s] is up to date" % code)
            return []

        symbol = self.codeToStockSymbol(code)
        print("[Download Stock Bars][%s] From %s to %s" % (symbol, startDate, endDate))
        bars = self.getHistory(symbol, "1d", startDate, endDate)
        instruments = self.getHistoryInstruments(symbol, None, startDate, endDate)

        '''
        stock bar does not contains adj_factor, get it from instruments
        '''
        bars = [self.rawDataToModel(code, bar) for bar in bars]
        for instrument in instruments:
            for bar in bars:
                if instrument['trade_date'] == bar.trade_date:
                    bar.adj_factor = instrument['adj_factor']
                    bar.sec_level = instrument['sec_level']
                    bar.is_suspended = instrument['is_suspended']
                    bar.position = instrument['position']
                    bar.upper_limit = instrument['upper_limit']
                    bar.lower_limit = instrument['lower_limit']

        # self.stockBarDao.addAll(bars)
        print("[Download Stock Bars][%s] count = %d\n" %(symbol, len(bars)))
        return bars

    def downloadAll(self):
        stocks = self.stockDao.getStockList()
        temp = []
        for code in stocks:
            bars = self.downloadBars(code)
            temp.extend(bars)
            if len(temp) > 200:
                self.stockDao.bulkSave(temp)
                temp = []
            if len(bars):
                time.sleep(0.05)


if __name__ == "__main__":
    spider = StockDailyBarAdjustNoneSpider()
    spider.downloadBars('000001')
