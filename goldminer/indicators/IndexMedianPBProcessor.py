# coding: utf-8
from datetime import datetime, timedelta

from goldminer.common.Utils import Utils
from goldminer.common.logger import get_logger
from goldminer.indicators.IndexPEPBBaseProcessor import IndexPEPBBaseProcessor
from goldminer.models.models import IndexPrimaryIndicator, TradingDerivativeIndicator
from goldminer.storage.TradingDerivativeIndicatorDao import TradingDerivativeIndicatorDao

logger = get_logger(__name__)


class IndexMedianPBProcessor(IndexPEPBBaseProcessor):

    def __init__(self):
        super(IndexMedianPBProcessor, self).__init__()
        self.fieldName = "median_pb"
        self.tradingDerivativeDao = TradingDerivativeIndicatorDao()

    def calcIndicatorByDate(self, indexCode, d):
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

        pbs = [p for p in stockPB if p > 0]
        pbs.sort()
        if len(pbs) == 0:
            print("Index {} has no pb > 0 at date {}, constituents={}", indexCode, d, constituents)
        else:
            pb = Utils.getMedian(pbs)
            model.median_pb = pb
            return model

    def process(self, indexCode):
        d = self.getStartDate(indexCode)
        if d is None:
            logger.error("Invalid start date, code = {}".format(indexCode))
            return

        now = datetime.now().date()
        models = []
        logger.info("Start calculate Median PB for {} from {} to {} ".format(indexCode, d, now))
        while d <= now:
            if self.stockManager.isTradeDate(d):
                model = self.calcIndicatorByDate(indexCode, d)
                if model:
                    models.append(model)
            d = d + timedelta(days=1)

        logger.info("{} median pb generated".format(len(models)))
        self.indexPrimaryIndicatorDao.bulkSave(models)
        logger.info("End calculate Median PB for {}".format(indexCode))


if __name__ == "__main__":
    manager = IndexMedianPBProcessor()
    manager.process('000913')
