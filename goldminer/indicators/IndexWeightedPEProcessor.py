# coding: utf-8
import math
from decimal import Decimal

from goldminer.common import GMConsts
from goldminer.common.Utils import Utils
from goldminer.common.logger import get_logger
from goldminer.indicators.IndexPEPBProcessor import IndexPEPBProcessor
from goldminer.storage.TradingDerivativeIndicatorDao import TradingDerivativeIndicatorDao

logger = get_logger(__name__)


class IndexWeightedPEProcessor(IndexPEPBProcessor):

    def __init__(self):
        super(IndexWeightedPEProcessor, self).__init__()
        self.fieldName = "weighted_pe"
        self.tradingDerivativeDao = TradingDerivativeIndicatorDao()

    def calculatePEPBIndicator(self, pepbList, **params):
        indexCode = params['indexCode']
        d = params['date']
        constituents = params['constituents']
        pepbDict = params['pepbDict']
        totalMarketValueDict = params['totalMarketValueDict']

        profitSum = 0
        totalMarketValueSum = 0

        for stock in constituents:

            if stock not in pepbDict:
                logger.warn("No pe found for stock {}, date {}".format(stock, d))
                continue

            if stock not in totalMarketValueDict:
                logger.warn("No total market value found for stock {}, date {}".format(stock, d))
                continue

            pe = pepbDict[stock]
            value = totalMarketValueDict[stock]

            if value < 1 or math.fabs(pe) < 1e-6:
                logger.warn("Invalid pe(=0) or total market value(<1), code {}, date {}, pe={}, total market value={}".
                            format(stock, d, pe, value))
                continue

            profit = value / Decimal(pe)
            profitSum += profit
            totalMarketValueSum += value

        # 处理指数的利润异常的情况
        # 1. 利润大于0，但是非常小，导致pe很大，限制pe为[0, GMConsts.ABNORMAL_MAX_PE]
        # 2. 利润等于0，pe记录为GMConsts.ABNORMAL_MAX_PE
        # 3. 利润小于0，pe记录为负数，限制范围[GMConsts.ABNORMAL_MIN_PE, 0]
        if profitSum > 0:
            pe = Utils.formatFloat(totalMarketValueSum / profitSum, 6)
            pe = min(pe, GMConsts.ABNORMAL_MAX_PE)
        elif profitSum == 0:
            pe = GMConsts.ABNORMAL_MAX_PE
        else:
            pe = Utils.formatFloat(totalMarketValueSum / profitSum, 6)
            pe = max(pe, GMConsts.ABNORMAL_MIN_PE)

        return pe


if __name__ == "__main__":
    peManager = IndexWeightedPEProcessor()
    peManager.process('000009')
