# coding: utf-8
from datetime import timedelta

from goldminer.indicators.IndexPEPBBaseProcessor import IndexPEPBBaseProcessor


class IndexMaxPBProcessor(IndexPEPBBaseProcessor):

    def __init__(self):
        super(IndexMaxPBProcessor, self).__init__()
        self.fieldName = "max_pb"

    def process(self, indexCode):
        d = self.getStartDate(indexCode)
        print("update max pb from %s" % d)
        if d is None:
            print("[Error] [%s] Invalid start date." % indexCode)
            return
        indicators = self.indexPrimaryIndicatorDao.getAfterDate(indexCode, d - timedelta(days=3))
        if len(indicators) == 0:
            print("[%s] max pb up to date." % indexCode)
            return

        maxPb = 0 if indicators[0].max_pb is None else indicators[0].max_pb
        count = 0
        changed = []
        for indicator in indicators:
            maxPb = max(maxPb, indicator.equal_weight_pb)
            if not indicator.max_pb:
                print("[%s] %s date=%s, pb=%f" % (indexCode, self.fieldName, indicator.trade_date, maxPb))
                indicator.max_pb = maxPb
                changed.append(indicator)
                count += 1

        if count > 0:
            self.indexPrimaryIndicatorDao.bulkSave(changed)
            print("[%s] %d max pb updated" % (indexCode, count))

        return count


if __name__ == "__main__":
    manager = IndexMaxPBProcessor()
    manager.process('000001')
