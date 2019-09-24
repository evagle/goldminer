# coding: utf-8
from collections import deque
from datetime import timedelta, datetime
from decimal import Decimal

from goldminer.common.logger import get_logger
from goldminer.indicators.IndexPEPBBaseProcessor import IndexPEPBBaseProcessor

logger = get_logger(__name__)


class IndexPEPBHeightProcessor(IndexPEPBBaseProcessor):

    def __init__(self):
        super(IndexPEPBHeightProcessor, self).__init__()
        self.heightFieldName = None
        self.baseFieldName = None

    def runEqualWeightPEHeight(self):
        self.heightFieldName = "ew_pe_height_ten_year"
        self.baseFieldName = "equal_weight_pe"
        self.fieldName = self.baseFieldName

    def runEqualWeightPBHeight(self):
        self.heightFieldName = "ew_pb_height_ten_year"
        self.baseFieldName = "equal_weight_pb"
        self.fieldName = self.baseFieldName

    def runWeightedPEHeight(self):
        self.heightFieldName = "w_pe_height_ten_year"
        self.baseFieldName = "weighted_pe"
        self.fieldName = self.baseFieldName

    def runWeightedPBHeight(self):
        self.heightFieldName = "w_pb_height_ten_year"
        self.baseFieldName = "weighted_pb"
        self.fieldName = self.baseFieldName

    def buildAllHeightIndicators(self, indexCode):
        indicators = self.indexPrimaryIndicatorDao.getByCode(indexCode)

        self.runEqualWeightPEHeight()
        self.process(indexCode, indicators)

        self.runEqualWeightPBHeight()
        self.process(indexCode, indicators)

        self.runWeightedPEHeight()
        self.process(indexCode, indicators)

        self.runWeightedPBHeight()
        self.process(indexCode, indicators)

    def process(self, indexCode, indexPrimaryIndicators=None):
        logger.info("[{}] Start processing {} ".format(indexCode, self.heightFieldName))

        if not indexPrimaryIndicators:
            indicators = self.indexPrimaryIndicatorDao.getByCode(indexCode)
        else:
            indicators = indexPrimaryIndicators

        if len(indicators) == 0:
            logger.error("[{}] No primary indicators found.".format(indexCode))
            return
        changed = []
        queue = deque()
        date_queue = deque()
        logger.info("[{}] 111 ".format(indexCode))
        for current in indicators:
            cur_val = getattr(current, self.baseFieldName)
            if cur_val is not None:
                queue.append(cur_val)
                date_queue.append(current.trade_date)
                if (current.trade_date - date_queue[0]).days > 3650:
                    queue.popleft()
                    date_queue.popleft()
            else:
                continue

            # If field(w_pb/pe_height_ten_year) is not None, no need to calculate
            if getattr(current, self.heightFieldName) is not None:
                continue
            logger.info("[{}] 222 ".format(indexCode))
            totalCount = len(queue)
            logger.info("[{}] 333 ".format(indexCode))
            smallerCount = 0

            for v in queue:
                if v < cur_val:
                    smallerCount += 1
            logger.info("[{}] 444 ".format(indexCode))

            if totalCount == 0:
                continue
            percent = smallerCount * 100 / totalCount
            height = float(Decimal(percent).quantize(Decimal('0.0')))
            setattr(current, self.heightFieldName, height)
            changed.append(current)

            logger.info("[{}] New value for {}, date={}, base={}, height={}({}/{})".format(
                indexCode, self.heightFieldName, current.trade_date, getattr(current, self.baseFieldName),
                height, smallerCount, totalCount
            ))

        if len(changed) > 0:
            self.indexPrimaryIndicatorDao.bulkSave(changed)
            logger.info("[{}] {} value updated for field {}".format(indexCode, len(changed), self.heightFieldName))
        else:
            logger.info("[{}] {} is up to date".format(indexCode, self.heightFieldName))
        return 0


if __name__ == "__main__":
    manager = IndexPEPBHeightProcessor()
    manager.buildAllHeightIndicators('000021')
