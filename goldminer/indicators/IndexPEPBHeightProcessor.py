# coding: utf-8
from datetime import timedelta, datetime
from decimal import Decimal

from goldminer.indicators.IndexPEPBBaseProcessor import IndexPEPBBaseProcessor


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
        d = self.getStartDate(indexCode)
        print("[%s] Update %s from %s" % (indexCode, self.heightFieldName, d))

        if d is None:
            print("[Error] [%s] Invalid start date." % indexCode)
            return

        indicators = self.indexPrimaryIndicatorDao.getByCode(indexCode)
        if len(indicators) == 0:
            print("[%s] no data found." % indexCode)
            return

        changed = []
        queue = []
        date_queue = []
        for current in indicators:
            # If field(w_pb/pe_height_ten_year) is not None, no need to calculate
            if getattr(current, self.heightFieldName) is not None:
                continue
            # If base field(weighted_pb/pe) is None, no need to calculate
            if getattr(current, self.baseFieldName) is None:
                continue

            if hasattr(current, self.baseFieldName) and getattr(current, self.baseFieldName) is not None:
                val = getattr(current, self.baseFieldName)
                queue.append(val)
                date_queue.append(current.trade_date)
                if (current.trade_date - date_queue[0]).days > 3650:
                    queue.pop(0)
                    date_queue.pop(0)

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

            print(
                "[%s] %s %s pe=%f, less=%d, total=%d, height=%f" % (indexCode, self.heightFieldName, current.trade_date,
                                                                    getattr(current, self.baseFieldName), smallerCount,
                                                                    totalCount, height))

        if len(changed) > 0:
            self.indexPrimaryIndicatorDao.bulkSave(changed)
            print("[%s] %d %s updated" % (indexCode, len(changed), self.heightFieldName))

        return 0


if __name__ == "__main__":
    manager = IndexPEPBHeightProcessor()
    manager.runWeightedPBHeight()
    manager.process('399001')
