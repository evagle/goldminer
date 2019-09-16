# coding: utf-8

from goldminer.common.Utils import Utils
from goldminer.common.logger import get_logger
from goldminer.indicators.IndexPEPBProcessor import IndexPEPBProcessor
from goldminer.storage.TradingDerivativeIndicatorDao import TradingDerivativeIndicatorDao

logger = get_logger(__name__)


class IndexEqualWeightPBProcessor(IndexPEPBProcessor):
    def __init__(self):
        super(IndexEqualWeightPBProcessor, self).__init__()
        self.fieldName = "equal_weight_pb"
        self.tradingDerivativeDao = TradingDerivativeIndicatorDao()

    def calculatePEPBIndicator(self, pepbList):
        # TODO 需要研究一下用filter之前的count还是之后的
        c = len(pepbList)
        pepbList = Utils.iqrFilter(pepbList)
        pbSum = sum([1 / p if p > 0 else 0 for p in pepbList])
        if pbSum == 0:
            return None
        else:
            pe = Utils.formatFloat(c / pbSum, 6)
            return pe


if __name__ == "__main__":
    manager = IndexEqualWeightPBProcessor()
    manager.process('399002')
