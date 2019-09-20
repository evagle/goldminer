# coding: utf-8
import math
from decimal import Decimal

from goldminer.common.Utils import Utils
from goldminer.common.logger import get_logger
from goldminer.indicators.IndexPEPBProcessor import IndexPEPBProcessor
from goldminer.storage.TradingDerivativeIndicatorDao import TradingDerivativeIndicatorDao

logger = get_logger(__name__)


class IndexWeightedPBProcessor(IndexPEPBProcessor):
    def __init__(self):
        super(IndexWeightedPBProcessor, self).__init__()
        self.fieldName = "weighted_pb"
        self.tradingDerivativeDao = TradingDerivativeIndicatorDao()

    def calculatePEPBIndicator(self,  pepbList, **params):
        indexCode = params['indexCode']
        d = params['date']
        constituents = params['constituents']
        pepbDict = params['pepbDict']
        totalMarketValueDict = params['totalMarketValueDict']

        netAssetsSum = 0
        totalMarketValueSum = 0

        for stock in constituents:
            if stock not in pepbDict:
                logger.warn("No pb found for stock {}, date {}".format(stock, d))
                continue

            if stock not in totalMarketValueDict:
                logger.warn("No total market value found for stock {}, date {}".format(stock, d))
                continue

            pb = pepbDict[stock]
            value = totalMarketValueDict[stock]

            if value < 1 or math.fabs(pb) < 1e-6:
                logger.warn(
                    "Invalid pb(=0) or total market value(<1), code {}, date {}, pe={}, total market value={}".
                        format(stock, d, pb, value))
                continue

            netAsset = value / Decimal(pb)
            netAssetsSum += netAsset
            totalMarketValueSum += value

        if netAssetsSum > 0:
            pb = Utils.formatFloat(totalMarketValueSum / netAssetsSum, 6)
            return pb
        else:
            logger.warn("code {}, date {} skipping weighted pb because net assets < 0".format(indexCode, d))
            return None


if __name__ == "__main__":
    peManager = IndexWeightedPBProcessor()
    peManager.process('000009')
