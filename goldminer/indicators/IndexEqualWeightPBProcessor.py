# coding: utf-8
from datetime import datetime, timedelta

from goldminer.common.Utils import Utils
from goldminer.common.logger import get_logger
from goldminer.indicators.IndexPEPBBaseProcessor import IndexPEPBBaseProcessor
from goldminer.models.models import IndexPrimaryIndicator, TradingDerivativeIndicator
from goldminer.storage.TradingDerivativeIndicatorDao import TradingDerivativeIndicatorDao


logger = get_logger(__name__)


class IndexEqualWeightPBProcessor(IndexPEPBBaseProcessor):
    def __init__(self):
        super(IndexEqualWeightPBProcessor, self).__init__()
        self.fieldName = "equal_weight_pb"
        self.tradingDerivativeDao = TradingDerivativeIndicatorDao()

    def calcIndicatorByDate(self, indexCode, d):
        logger.info("IndexEqualWeightPB started code={}, date={}".format(indexCode, d))
        model = self.indexPrimaryIndicatorDao.getByDate(indexCode, d)
        if model is None:
            model = IndexPrimaryIndicator()
            model.code = indexCode
            model.trade_date = d

        constituents = self.indexConstituentManager.getConstituents(indexCode, d)
        pbDict = self.tradingDerivativeDao.getColumnValuesByDate(d, TradingDerivativeIndicator.PB)

        if constituents is None:
            logger.warn("No constituent found for code {} date {}".format(indexCode, d))
            return None
        stockPB = []
        for stock in constituents:
            if stock in pbDict:
                stockPB.append(pbDict[stock])

        pbsum = sum([1 / p if p > 0 else 0 for p in stockPB])
        if pbsum > 0:
            pb = Utils.formatFloat(len(stockPB) / pbsum, 6)
            model.equal_weight_pb = pb
            return model
        else:
            logger.warn("pbsum is < 0, indexCode = {} d = {}".format(indexCode, d))
            return None

    def process(self, indexCode):
        d = self.getStartDate(indexCode)
        if d is None:
            logger.error("Invalid start date, code = {}".format(indexCode))
            return

        now = datetime.now().date()
        models = []
        logger.info("Start calcEqualWeightedPB for {} from {} to {} ".format(indexCode, d, now))
        while d <= now:
            if self.stockManager.isTradeDate(d):
                model = self.calcIndicatorByDate(indexCode, d)
                if model:
                    models.append(model)
            d = d + timedelta(days=1)

        self.indexPrimaryIndicatorDao.bulkSave(models)
        logger.info("End calcEqualWeightedPE for {}, save {} equal weight pe".format(indexCode, len(models)))

        return models


if __name__ == "__main__":
    manager = IndexEqualWeightPBProcessor()
    manager.process('000913')


