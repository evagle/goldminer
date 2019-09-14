# coding: utf-8
from datetime import datetime, timedelta

from goldminer.common.Utils import Utils
from goldminer.common.logger import get_logger
from goldminer.indicators.IndexPEPBBaseProcessor import IndexPEPBBaseProcessor
from goldminer.models.models import IndexPrimaryIndicator, TradingDerivativeIndicator
from goldminer.storage.TradingDerivativeIndicatorDao import TradingDerivativeIndicatorDao

logger = get_logger(__name__)


class IndexMedianPEProcessor(IndexPEPBBaseProcessor):
    def __init__(self):
        super(IndexMedianPEProcessor, self).__init__()
        self.fieldName = "median_pe"
        self.tradingDerivativeDao = TradingDerivativeIndicatorDao()

    def calcIndicatorByDate(self, indexCode, d):
        model = self.indexPrimaryIndicatorDao.getByDate(indexCode, d)
        if model is None:
            model = IndexPrimaryIndicator()
            model.code = indexCode
            model.trade_date = d

        constituents = self.indexConstituentManager.getConstituents(indexCode, d)
        peDict = self.tradingDerivativeDao.getColumnValuesByDate(d, TradingDerivativeIndicator.PETTM)

        if constituents is None:
            logger.warn("No constituent found for code {} date {}".format(indexCode, d))
            return None

        stockPETTM = []
        for stock in constituents:
            if stock in peDict:
                stockPETTM.append(peDict[stock])

        pes = [p for p in stockPETTM if p > 0]
        pes.sort()
        if len(pes) == 0:
            print("Index {} has no pe > 0 at date {}, constituents={}", indexCode, d, constituents)
            return None
        else:
            pe = Utils.getMedian(pes)
            model.median_pe = pe
            return model

    def process(self, indexCode):
        d = self.getStartDate(indexCode)
        if d is None:
            logger.error("Invalid start date, code = {}".format(indexCode))
            return

        now = datetime.now().date()
        models = []
        logger.info("Start calculate Median PE for {} from {} to {} ".format(indexCode, d, now))
        while d <= now:
            if self.stockManager.isTradeDate(d):
                model = self.calcIndicatorByDate(indexCode, d)
                if model:
                    models.append(model)
            d = d + timedelta(days=1)

        logger.info("{} median pe generated".format(len(models)))
        self.indexPrimaryIndicatorDao.bulkSave(models)
        logger.info("End calculate Median PE for {}".format(indexCode))

        return models


if __name__ == "__main__":
    peManager = IndexMedianPEProcessor()
    peManager.process('000001')


