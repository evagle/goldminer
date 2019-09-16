# coding: utf-8

from goldminer.common.Utils import Utils
from goldminer.common.logger import get_logger
from goldminer.indicators.IndexPEPBProcessor import IndexPEPBProcessor
from goldminer.storage.TradingDerivativeIndicatorDao import TradingDerivativeIndicatorDao

logger = get_logger(__name__)


class IndexMedianPBProcessor(IndexPEPBProcessor):

    def __init__(self):
        super(IndexMedianPBProcessor, self).__init__()
        self.fieldName = "median_pb"
        self.tradingDerivativeDao = TradingDerivativeIndicatorDao()

    def calculatePEPBIndicator(self, pepbList):
        pbs = [p for p in pepbList if p > 0]
        pbs.sort()
        if len(pbs) == 0:
            return None
        else:
            return Utils.getMedian(pbs)


if __name__ == "__main__":
    manager = IndexMedianPBProcessor()
    manager.process('399002')
