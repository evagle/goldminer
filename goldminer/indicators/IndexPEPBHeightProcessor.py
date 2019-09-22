# coding: utf-8
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

    def process(self, indexCode):
        logger.info("[{}] Start processing {} ".format(indexCode, self.heightFieldName))

        indicators = self.indexPrimaryIndicatorDao.getByCode(indexCode)
        if len(indicators) == 0:
            logger.error("[{}] No primary indicators found.".format(indexCode))
            return

        changed = []
        queue = []
        date_queue = []
        for current in indicators:
            if getattr(current, self.baseFieldName) is not None:
                val = getattr(current, self.baseFieldName)
                queue.append(val)
                date_queue.append(current.trade_date)
                if (current.trade_date - date_queue[0]).days > 3650:
                    queue.pop(0)
                    date_queue.pop(0)
            else:
                continue

            # If field(w_pb/pe_height_ten_year) is not None, no need to calculate
            if getattr(current, self.heightFieldName) is not None:
                continue

            totalCount = len(queue)
            smallerCount = 0
            cur_val = getattr(current, self.baseFieldName)
            for v in queue:
                if v < cur_val:
                    smallerCount += 1

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
    manager.runWeightedPBHeight()
    manager.process('000001')
