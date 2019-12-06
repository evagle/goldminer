# coding: utf-8
import math
from datetime import datetime, timedelta

from goldminer.common.Utils import Utils

from goldminer.common.logger import get_logger
from goldminer.indicators.BaseIndicatorProcessor import BaseIndicatorProcessor
from goldminer.models.models import StockCustomIndicator
from goldminer.storage.StockCustomIndicatorDao import StockCustomIndicatorDao
from goldminer.storage.StockDailyBarAdjustNoneDao import StockDailyBarAdjustNoneDao
from goldminer.storage.StockDao import StockDao

logger = get_logger(__name__)


class NDayGainsProcessor(BaseIndicatorProcessor):
    def __init__(self):
        self.stockBarNoneDao = StockDailyBarAdjustNoneDao()
        self.stockDao = StockDao()
        self.customIndicatorDao = StockCustomIndicatorDao()

    def process(self, code, **kwargs):
        latestDate = self.customIndicatorDao.getLatestDate(code, columnName='gain50') + timedelta(days=1)
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
        limit = (endDate - startDate).days + 300
        
        bars = self.stockBarNoneDao.getN(code, limit=limit, adjust="prev")
        bars.reverse()
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
                for j in range(min(10, i - n + 1)):
                    close = bars[i - n + j].close
                    if close > 0:
                        break

                gain = (bars[i].close - close) / close * 100 if close > 0 else 0
                gain = Utils.formatFloat(gain, 6)
                attr = "gain" + str(n)
                oldval = getattr(model, attr)
                if oldval is None or math.fabs(oldval - gain) > 1e-6:
                    setattr(model, attr, gain)
                    customIndicatorsChanged[(code, model.trade_date)] = model

        logger.info("code {} has {} bars updates".format(code, len(customIndicatorsChanged)))
        self.customIndicatorDao.bulkSave(customIndicatorsChanged.values())
        logger.info("End NDayGains code {}  ".format(code))

    def updateAll(self):
        stocks = self.stockDao.getStockList(includeDelisted=True)
        for code in stocks:
            self.process(code)


if __name__ == "__main__":
    stockDao = StockDao()
    stocks = stockDao.getStockList()
    processor = NDayGainsProcessor()
    processor.process('000002')
