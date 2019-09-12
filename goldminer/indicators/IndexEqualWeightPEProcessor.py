# coding: utf-8
from datetime import datetime, timedelta

from goldminer.common.Utils import Utils
from goldminer.common.logger import get_logger
from goldminer.indicators.IndexPEPBBaseProcessor import IndexPEPBBaseProcessor
from goldminer.models.models import IndexPrimaryIndicator, TradingDerivativeIndicator
from goldminer.storage.TradingDerivativeIndicatorDao import TradingDerivativeIndicatorDao

logger = get_logger(__name__)


class IndexEqualWeightPEProcessor(IndexPEPBBaseProcessor):
    def __init__(self):
        super(IndexEqualWeightPEProcessor, self).__init__()
        self.fieldName = "equal_weight_pe"
        self.tradingDerivativeDao = TradingDerivativeIndicatorDao()

    def calcIndicatorByDate(self, indexCode, d):
        logger.info("IndexEqualWeightPE started code={}, date={}".format(indexCode, d))
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

        stockCount = len(stockPETTM)
        stockPETTM = Utils.iqrFilter(stockPETTM)

        peSum = sum([1 / p if p > 0 else 0 for p in stockPETTM])
        if peSum == 0:
            logger.error("pbsum is <= 0, indexCode = {} d = {}".format(indexCode, d))
            return None
        else:
            pe = Utils.formatFloat(stockCount / peSum, 6)
            model.equal_weight_pe = pe
            return model

    def process(self, indexCode):
        d = self.getStartDate(indexCode)
        if d is None:
            logger.error("Invalid start date, code = ", indexCode)
            return

        now = datetime.now().date()
        models = []
        logger.info("Start calcEqualWeightedPE for {} from {} to {} ".format(indexCode, d, now))
        while d <= now:
            if self.stockManager.isTradeDate(d):
                model = self.calcIndicatorByDate(indexCode, d)
                if model:
                    models.append(model)
            d = d + timedelta(days=1)

        logger.info("End calcEqualWeightedPE for {}, save {} equal weight pe".format(indexCode, len(models)))
        self.indexPrimaryIndicatorDao.bulkSave(models)

        return models


if __name__ == "__main__":
    peManager = IndexEqualWeightPEProcessor()
    peManager.process('000001')
