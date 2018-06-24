# coding: utf-8
from datetime import timedelta

from evaluation.IndexPEPBBaseProcessor import IndexPEPBBaseProcessor


class IndexMaxPEProcessor(IndexPEPBBaseProcessor):

    def __init__(self):
        super(IndexMaxPEProcessor, self).__init__()
        self.fieldName = "max_pe"

    def process(self, indexCode):
        d = self.getStartDate(indexCode)
        print("[%s] Update %s from %s" % (indexCode, self.fieldName, d))
        if d is None:
            print("[Error] [%s] Invalid start date." % indexCode)
            return
        indicators = self.indexPrimaryIndicatorDao.getAfterDate(indexCode, d - timedelta(days=3))
        if len(indicators) == 0:
            print("[%s] max pe up to date." % indexCode)
            return

        maxPe = 0 if indicators[0].max_pe is None else indicators[0].max_pe
        count = 0
        changed = []
        for indicator in indicators:
            maxPe = max(maxPe, indicator.equal_weight_pe)
            print("maxPe", maxPe, indicator.trade_date)
            if not indicator.max_pe:
                indicator.max_pe = maxPe
                changed.append(indicator)
                # self.indexPrimaryIndicatorDao.add(indicator)
                count += 1

        if count > 0:
            self.indexPrimaryIndicatorDao.bulkSave(changed)
            print("[%s] %d max pe updated" % (indexCode, count))

        return count


if __name__ == "__main__":
    peManager = IndexMaxPEProcessor()
    peManager.process('000001')


