# coding: utf-8
from datetime import timedelta, datetime
from decimal import Decimal

from evaluation.IndexPEPBBaseProcessor import IndexPEPBBaseProcessor


class IndexPBHeightTenYearProcessor(IndexPEPBBaseProcessor):

    def __init__(self):
        super(IndexPBHeightTenYearProcessor, self).__init__()
        self.fieldName = "pb_height_ten_year"

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
            if current.pb_height_ten_year is not None:
                continue
            tenYearBefore = current.trade_date - timedelta(days=3650)
            totalCount = 0
            smallerCount = 0
            for i in indicators:
                if i.trade_date >= tenYearBefore and i.trade_date < current.trade_date:
                    totalCount += 1
                    if i.equal_weight_pb <= current.equal_weight_pb:
                        smallerCount += 1
            if totalCount == 0:
                continue
            percent = smallerCount * 100 / totalCount
            current.pb_height_ten_year = float(Decimal(percent).quantize(Decimal('0.0')))
            print("[%s] %s %s pb=%f, less=%d, total=%d, height=%f" % (indexCode, self.fieldName, current.trade_date, current.equal_weight_pb, smallerCount,
                  totalCount, current.pb_height_ten_year))

            changed.append(current)

        if len(changed) > 0:
            self.indexPrimaryIndicatorDao.bulkSave(changed)
            print("[%s] %d %s updated" % (indexCode, len(changed), self.fieldName))

        return 0


if __name__ == "__main__":
    manager = IndexPBHeightTenYearProcessor()
    manager.process('000001')
