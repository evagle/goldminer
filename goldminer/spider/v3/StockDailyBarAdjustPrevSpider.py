# coding=utf-8
import time
from datetime import timedelta, datetime

from goldminer.common import GMConsts
from goldminer.common.logger import get_logger
from goldminer.models.models import StockDailyBarAdjustPrev
from goldminer.spider.v3.GMBaseSpiderV3 import GMBaseSpiderV3
from goldminer.storage.StockDailyBarAdjustPrevDao import StockDailyBarAdjustPrevDao
from goldminer.storage.StockDao import StockDao

logger = get_logger(__name__)


class StockDailyBarAdjustPrevSpider(GMBaseSpiderV3):

    def __init__(self):
        super(StockDailyBarAdjustPrevSpider, self).__init__()
        self.stockBarDao = StockDailyBarAdjustPrevDao()
        self.stockDao = StockDao()

    def rawDataToModel(self, code, rawBar):
        model = self._rawDataToModel(rawBar, StockDailyBarAdjustPrev)
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

        if startDate > datetime.now().date():
            logger.info("[%s] is up to date" % code)
            return

        symbol = self.codeToStockSymbol(code)
        logger.info("[Download Stock Bars][%s] From %s to %s" % (symbol, startDate, endDate))
        bars = self.getHistory(symbol, "1d", startDate, endDate, adjust=GMConsts.ADJUST_PREV)
        instruments = self.getHistoryInstruments(symbol, None, startDate, endDate)

        '''
        stock bar does not contains adj_factor, get it from instruments
        '''
        bars = [self.rawDataToModel(code, bar) for bar in bars]
        for instrument in instruments:
            for bar in bars:
                if instrument['trade_date'].date() == bar.trade_date:
                    bar.adj_factor = instrument['adj_factor']
                    bar.sec_level = instrument['sec_level']
                    bar.is_suspended = instrument['is_suspended']
                    bar.position = instrument['position']

        self.stockBarDao.addAll(bars)
        logger.info("[Download Stock Bars][%s] count = %d\n" % (symbol, len(bars)))
        return bars

    def downloadAll(self):
        stocks = self.stockDao.getStockList()
        for code in stocks:
            if self.downloadBars(code) is not None:
                time.sleep(0.05)


if __name__ == "__main__":
    spider = StockDailyBarAdjustPrevSpider()
    spider.downloadBars('601313')
