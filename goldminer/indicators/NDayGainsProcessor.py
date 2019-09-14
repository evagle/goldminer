# coding: utf-8
import math
from datetime import datetime, timedelta

from goldminer.common.logger import get_logger
from goldminer.indicators.BaseIndicatorProcessor import BaseIndicatorProcessor
from goldminer.models.models import StockCustomIndicator
from goldminer.storage.StockCustomIndicatorDao import StockCustomIndicatorDao
from goldminer.storage.StockDailyBarAdjustPrevDao import StockDailyBarAdjustPrevDao
from goldminer.storage.StockDao import StockDao


logger = get_logger(__name__)


class NDayGainsProcessor(BaseIndicatorProcessor):
    def __init__(self):
        self.stockBarPrevDao = StockDailyBarAdjustPrevDao()
        self.stockDao = StockDao()
        self.customIndicatorDao = StockCustomIndicatorDao()

    def process1(self, code):
        latestDate = self.customIndicatorDao.getLatestDate(code, columnName='gain50')
        startDate = latestDate
        endDate = datetime.today().date()
        if startDate == endDate:
            logger.info("{} NDayGain is up to date".format(code))
            return
        logger.info("Processing NDayGains for code {}, from {} to {}".format(code, startDate, endDate))

        modelsInDB = self.customIndicatorDao.getByDateRange(code, startDate, endDate)
        modelsDict = {}
        for model in modelsInDB:
            modelsDict[(model.code, model.trade_date)] = model

        customIndicatorsChanged = {}
        bars = self.stockBarPrevDao.getAll(code)
        for i in range(len(bars)):
            key = (code, bars[i].trade_date)
            if key in modelsDict:
                model = modelsDict[key]
            else:
                model = StockCustomIndicator()
                model.code = code
                model.trade_date = bars[i].trade_date

            for n in [50, 120, 250]:
                if i < n:
                    continue

                bar = bars[i]
                if bar.trade_date < startDate:
                    continue

                # close可能等于零，此时找后面的几个bar
                close = 0
                for j in range(min(10, i-n+1)):
                    close = bars[i - n + j].close
                    if close > 0:
                        break

                gain = (bars[i].close - close) / close * 100 if close > 0 else 0
                attr = "gain" + str(n)
                oldval = getattr(model, attr)
                if oldval is None or math.fabs(oldval - gain) > 1e-6:
                    setattr(model, attr, gain)
                    customIndicatorsChanged[(code, model.trade_date)] = model

        logger.info("End NDayGains code {} has {} updates".format(code, len(customIndicatorsChanged)))
        self.customIndicatorDao.bulkSave(customIndicatorsChanged.values())

    def process(self, code, **kwargs):
        '''

        :param code:
        :param kwargs:
                    n: int, n days
                    refresh: bool, refresh all data
        :return:
        '''
        n = self.get_args(kwargs, "n", 0)
        refresh = self.get_args(kwargs, "refresh", False)

        if n > 50:
            bars = self.stockBarPrevDao.getN(code, n)
        else:
            bars = self.stockBarPrevDao.getAll(code)

        changedBars = []
        for n in [50, 120, 250]:
            for i in range(n, len(bars)):
                attr = "gain" + str(n)

                # close可能等于零，此时找后面的几个bar
                close = 0
                for j in range(10):
                    close = bars[i - n + j].close
                    if close > 0:
                        break
                    else:
                        print("Error bar close = 0", bars[i - n + j])

                val = (bars[i].close - close) / close * 100 if close > 0 else 0

                oldval = getattr(bars[i], attr)
                if refresh or oldval is None or math.fabs(oldval-val) > 1e-6:
                    setattr(bars[i], attr, val)
                    changedBars.append(bars[i])

        print(len(changedBars), "bars updated")
        self.stockBarPrevDao.bulkSave(changedBars)

    def updateAll(self):
        stocks = self.stockDao.getStockList()
        for code in stocks:
            self.process1(code)

if __name__ == "__main__":
    stockDao = StockDao()
    stocks = stockDao.getStockList()
    processor = NDayGainsProcessor()
    processor.process1('000001')