# coding: utf-8

from goldminer.common.Utils import Utils
from goldminer.common.logger import get_logger
from goldminer.indicators.IndexPEPBProcessor import IndexPEPBProcessor
from goldminer.storage.TradingDerivativeIndicatorDao import TradingDerivativeIndicatorDao

logger = get_logger(__name__)


class IndexEqualWeightPEProcessor(IndexPEPBProcessor):
    def __init__(self):
        super(IndexEqualWeightPEProcessor, self).__init__()
        self.fieldName = "equal_weight_pe"
        self.tradingDerivativeDao = TradingDerivativeIndicatorDao()

    def calculatePEPBIndicator(self, pepbList, **params):
        # TODO 需要研究一下用filter之前的count还是之后的
        c = len(pepbList)
        pepbList = Utils.iqrFilter(pepbList)
        peSum = sum([1 / p if p > 0 else 0 for p in pepbList])
        if peSum == 0:
            return None
        else:
            pe = Utils.formatFloat(c / peSum, 6)
            return pe


if __name__ == "__main__":
    peManager = IndexEqualWeightPEProcessor()
    peManager.process('399002')
