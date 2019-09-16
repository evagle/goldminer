# coding: utf-8

from goldminer.common.Utils import Utils
from goldminer.common.logger import get_logger
from goldminer.indicators.IndexPEPBProcessor import IndexPEPBProcessor
from goldminer.storage.TradingDerivativeIndicatorDao import TradingDerivativeIndicatorDao

logger = get_logger(__name__)


class IndexMedianPEProcessor(IndexPEPBProcessor):
    def __init__(self):
        super(IndexMedianPEProcessor, self).__init__()
        self.fieldName = "median_pe"
        self.tradingDerivativeDao = TradingDerivativeIndicatorDao()

    def calculatePEPBIndicator(self, pepbList):
        pes = [p for p in pepbList if p > 0]
        pes.sort()
        if len(pes) == 0:
            return None
        else:
            return Utils.getMedian(pes)


if __name__ == "__main__":
    peManager = IndexMedianPEProcessor()
    peManager.process('399002')
