# coding=utf-8
import time
from datetime import timedelta, datetime

from common import GMConsts
from models.models import StockDailyBarAdjustPrev
from spider.v3.GMBaseSpiderV3 import GMBaseSpiderV3
from storage.StockDailyBarAdjustPrevDao import StockDailyBarAdjustPrevDao
from storage.StockDao import StockDao


class StockDailyBarAdjustPrevSpider(GMBaseSpiderV3):

    def __init__(self):
        super(StockDailyBarAdjustPrevSpider, self).__init__()
        self.stockBarDao = StockDailyBarAdjustPrevDao()
        self.stockDao = StockDao()

    def rawDataToModel(self, code, rawBar):
        model = self._rawDataToModel(code, rawBar, StockDailyBarAdjustPrev)
        model.code = code
        model.trade_date = rawBar['eob'].date()
        for key in ['pre_close', 'amount', 'open', 'close', 'high', 'low']:
            if getattr(model, key) is None:
                setattr(model, key, 0)
        return model

    def downloadBars(self, code):
        startDate = self.stockBarDao.getLatestDate(code) + timedelta(days=1)
        endDate = datetime.now() + timedelta(days=1)

        symbol = self.codeToStockSymbol(code)
        print("[Download Stock Bars][%s] From %s to %s" % (symbol, startDate, endDate))
        bars = self.getHistory(symbol, "1d", startDate, endDate, adjust=GMConsts.ADJUST_PREV)
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

        self.stockBarDao.addAll(bars)
        print("[Download Stock Bars][%s] count = %d\n" %(symbol, len(bars)))
        return bars

    def downloadAll(self):
        stocks = self.stockDao.getStockList()
        for i in stocks:
            self.downloadBars(i)
            time.sleep(0.1)


if __name__ == "__main__":
    spider = StockDailyBarAdjustPrevSpider()
    spider.downloadBars('000001')
