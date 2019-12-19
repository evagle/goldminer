# coding=utf-8
from datetime import timedelta, datetime

from goldminer.common.Utils import Utils
from goldminer.common.logger import get_logger
from goldminer.models.models import StockDailyBar
from goldminer.spider.v3.GMBaseSpiderV3 import GMBaseSpiderV3
from goldminer.storage.StockDailyBarDao import StockDailyBarDao
from goldminer.storage.StockDao import StockDao

logger = get_logger(__name__)


class StockDailyBarSpider(GMBaseSpiderV3):

    def __init__(self):
        super(StockDailyBarSpider, self).__init__()
        self.stockBarDao = StockDailyBarDao()
        self.stockDao = StockDao()

    def raw_data_to_model(self, raw_bar):
        model = self._rawDataToModel(raw_bar, StockDailyBar)
        model.trade_date = raw_bar['eob'].date()
        model.code = self.symbolToCode(raw_bar['symbol'])
        for key in ['pre_close', 'amount', 'open', 'close', 'high', 'low']:
            if getattr(model, key) is None:
                setattr(model, key, 0)
        return model

    def download_bars(self, code):
        startDate = self.stockBarDao.getLatestDate(code) + timedelta(days=1)
        endDate = datetime.now() + timedelta(days=1)

        return self.download_bars_by_date_range(code, startDate, endDate)

    def download_bars_by_date_range(self, code, startDate, endDate):
        if startDate > datetime.now().date():
            logger.info("[%s] is up to date" % code)
            return []

        symbol = self.codeToStockSymbol(code)
        logger.info("[Download Stock Bars][%s] From %s to %s" % (symbol, startDate, endDate))
        bars = self.getHistory(symbol, "1d", startDate, endDate)
        instruments = self.getHistoryInstruments(symbol, None, startDate, endDate)

        '''
        stock bar does not contains adj_factor, get it from instruments
        '''
        bars = [self.raw_data_to_model(bar) for bar in bars]
        for instrument in instruments:
            for bar in bars:
                if instrument['trade_date'].date() == bar.trade_date:
                    bar.adj_factor = instrument['adj_factor']
                    bar.sec_level = instrument['sec_level']
                    bar.is_suspended = instrument['is_suspended']
                    bar.position = instrument['position']

        bars = list(filter(lambda bar: bar.adj_factor is not None, bars))

        logger.info("[Download Stock Bars][%s] count = %d\n" % (symbol, len(bars)))
        return bars

    def download_all(self):
        stocks = self.stockDao.getStockList()
        temp = []
        for code in stocks:
            bars = self.download_bars(code)
            temp.extend(bars)
            if len(temp) > 200:
                self.stockBarDao.bulkSave(temp)
                temp = []

    def fix_bars(self, code):
        start_date = Utils.maxDate(self.stockDao.getStockPublishDate(code), datetime(2005, 1, 1).date())
        end_date = datetime.now() + timedelta(days=1)

        bars = self.download_bars_by_date_range(code, start_date, end_date)

        adj_factor = self.stockBarDao.getAdjFactor(code)
        adj_factor_dict = {}
        for row in adj_factor:
            adj_factor_dict[(row[0], row[1])] = row[2]

        for bar in bars:
            if bar.adj_factor is None:
                if code != "001872" and bar.trade_date != datetime(2019, 2, 14).date():
                    bar.adj_factor = adj_factor_dict[(bar.code, bar.trade_date)]

        self.stockBarDao.insertOrReplace(bars)
        logger.info("Save {} bars for code {}\n".format(len(bars), code))


if __name__ == "__main__":
    spider = StockDailyBarSpider()
    codes_to_fix = ["000043", "001914"]
    for code in codes_to_fix:
        spider.fix_bars(code)
