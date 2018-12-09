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
            if getattr(model, key) is None or \
                    str(getattr(model, key)) == "inf" or \
                    str(getattr(model, key)) == "nan":
                setattr(model, key, 0)
        return model

    def downloadBars(self, code):
        startDate = self.stockBarDao.getLatestDate(code) + timedelta(days=1)
        endDate = datetime.now() + timedelta(days=1)

        if startDate >= datetime.now().date():
            print("[%s] is up to date" % code)
            return

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
        print("[Download Stock Bars][%s] count = %d\n" % (symbol, len(bars)))
        return bars

    def downloadAll(self):
        stocks = self.stockDao.getStockList()
        for i in stocks:
            if self.downloadBars(i) is not None:
                time.sleep(0.1)

    def checkBars(self, code):
        '''
        check if stock bar is with correct close price
        :param code:
        :return:
        '''
        bars = self.stockBarDao.getAll(code)
        incorrect = []
        for i in range(1, len(bars)):
            if bars[i].close > bars[i - 1].close * 1.15 or bars[i].close < bars[i - 1].close * 0.88:
                print("***", code, bars[i].close, bars[i-1].close)
                incorrect.append([bars[i-1], bars[i]])
        return incorrect


if __name__ == "__main__":
    spider = StockDailyBarAdjustPrevSpider()
    spider.downloadBars('601313')
