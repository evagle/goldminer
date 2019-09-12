# coding: utf-8
import math
from datetime import datetime, timedelta
from decimal import Decimal

from goldminer.common.Utils import Utils
from goldminer.common.logger import get_logger
from goldminer.indicators.IndexPEPBBaseProcessor import IndexPEPBBaseProcessor
from goldminer.models.models import IndexPrimaryIndicator, TradingDerivativeIndicator
from goldminer.storage.TradingDerivativeIndicatorDao import TradingDerivativeIndicatorDao


logger = get_logger(__name__)


class IndexWeightedPBProcessor(IndexPEPBBaseProcessor):
    def __init__(self):
        super(IndexWeightedPBProcessor, self).__init__()
        self.fieldName = "weighted_pb"
        self.tradingDerivativeDao = TradingDerivativeIndicatorDao()

    def calcIndicatorByDate(self, indexCode, d):

        model = self.indexPrimaryIndicatorDao.getByDate(indexCode, d)
        if model is None:
            model = IndexPrimaryIndicator()
            model.code = indexCode
            model.trade_date = d

        constituents = self.indexConstituentManager.getConstituents(indexCode, d)
        if constituents is None:
            logger.warn("No constituent found for code {} date {}".format(indexCode, d))
            return None

        netAssetsSum = 0
        totalMarketValueSum = 0
        pbDict = self.tradingDerivativeDao.getColumnValuesByDate(d, TradingDerivativeIndicator.PB)
        totalMarketValueDict = self.tradingDerivativeDao.getColumnValuesByDate(d,
                                                                               TradingDerivativeIndicator.TOTMKTCAP)

        for stock in constituents:
            if stock not in pbDict:
                logger.warn("No pb found for stock {}, date {}".format(stock, d))
                continue

            if stock not in totalMarketValueDict:
                logger.warn("No total market value found for stock {}, date {}".format(stock, d))
                continue

            pb = pbDict[stock]
            value = totalMarketValueDict[stock]

            if value < 1 or math.fabs(pb) < 1e-6:
                logger.warn(
                    "Invalid pb(=0) or total market value(<1), code {}, date {}, pe={}, total market value={}".
                    format(stock, d, pb, value))
                continue

            netAsset = value / Decimal(pb)
            netAssetsSum += netAsset
            totalMarketValueSum += value
        logger.debug("555")
        if netAssetsSum > 0:
            pb = Utils.formatFloat(totalMarketValueSum / netAssetsSum, 6)
            model.weighted_pb = pb
            logger.info("New weighted pb code {}, date {}, pb {}".format(indexCode, d, pb))
            return model
        else:
            logger.warn("code {}, date {} skipping weighted pb because net assets < 0".format(indexCode, d))
            return None



    def process(self, indexCode):
        d = self.getStartDate(indexCode)
        if d is None:
            print("[Error] Invalid start date, code = ", indexCode)
            return

        now = datetime.now().date()
        models = []
        print("[%s] calcWeightedPB from %s to %s " % (indexCode, d, now))
        while d <= now:
            if self.stockManager.isTradeDate(d):
                model = self.calcIndicatorByDate(indexCode, d)
                if model:
                    models.append(model)
            d = d + timedelta(days=1)

        logger.info("[%s] Save %d weighted pb" % (indexCode, len(models)))
        self.indexPrimaryIndicatorDao.bulkSave(models)

        return models


if __name__ == "__main__":
    peManager = IndexWeightedPBProcessor()
    peManager.process('000009')


