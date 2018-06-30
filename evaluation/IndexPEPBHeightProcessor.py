# coding: utf-8
from datetime import timedelta, datetime
from decimal import Decimal

from evaluation.IndexPEPBBaseProcessor import IndexPEPBBaseProcessor


class IndexPEPBHeightProcessor(IndexPEPBBaseProcessor):

    def __init__(self):
        super(IndexPEPBHeightProcessor, self).__init__()
        self.fieldName = None
        self.peName = None

    def runEqualWeightPEHeight(self):
        self.fieldName = "ew_pe_height_ten_year"
        self.peName = "equal_weight_pe"

    def runEqualWeightPBHeight(self):
        self.fieldName = "ew_pb_height_ten_year"
        self.peName = "equal_weight_pb"

    def runWeightedPEHeight(self):
        self.fieldName = "w_pe_height_ten_year"
        self.peName = "weighted_pe"

    def runWeightedPBHeight(self):
        self.fieldName = "w_pb_height_ten_year"
        self.peName = "weighted_pb"

    def process(self, indexCode):
        d = self.getStartDate(indexCode)
        print("[%s] Update %s from %s" % (indexCode, self.fieldName, d))

        if d is None:
            print("[Error] [%s] Invalid start date." % indexCode)
            return

        indicators = self.indexPrimaryIndicatorDao.getByCode(indexCode)
        if len(indicators) == 0:
            print("[%s] no data found." % indexCode)
            return

        changed = []
        for current in indicators:
            # if getattr(current, self.fieldName) is not None:
            #     continue
            tenYearBefore = current.trade_date - timedelta(days=3650)
            totalCount = 0
            smallerCount = 0
            for i in indicators:
                if tenYearBefore <= i.trade_date < current.trade_date:
                    totalCount += 1
                    if getattr(i, self.peName) <= getattr(current, self.peName):
                        smallerCount += 1
            if totalCount == 0:
                continue
            percent = smallerCount * 100 / totalCount
            height = float(Decimal(percent).quantize(Decimal('0.0')))
            setattr(current, self.fieldName, height)
            changed.append(current)

            print("[%s] %s %s pe=%f, less=%d, total=%d, height=%f" % (indexCode, self.fieldName, current.trade_date,
                                getattr(current, self.peName), smallerCount, totalCount, height))

        if len(changed) > 0:
            self.indexPrimaryIndicatorDao.bulkSave(changed)
            print("[%s] %d %s updated" % (indexCode, len(changed), self.fieldName))

        return 0


if __name__ == "__main__":
    manager = IndexPEPBHeightProcessor()
    manager.runWeightedPBHeight()
    manager.process('000009')

