# coding: utf-8
from datetime import timedelta

from goldminer.indicators.IndexPEPBBaseProcessor import IndexPEPBBaseProcessor


class IndexMaxPointProcessor(IndexPEPBBaseProcessor):

    def __init__(self):
        super(IndexMaxPointProcessor, self).__init__()
        self.fieldName = "max_point"

    def process(self, indexCode):
        d = self.getStartDate(indexCode)
        print("[%s] Update %s from %s" % (indexCode, self.fieldName, d))
        if d is None:
            print("[Error] [%s] Invalid start date." % indexCode)
            return
        indicators = self.indexPrimaryIndicatorDao.getAfterDate(indexCode, d - timedelta(days=3))
        if len(indicators) == 0:
            print("[%s] max point up to date." % indexCode)
            return

        maxPoint = -1 if indicators[0].max_point is None else indicators[0].max_point
        count = 0
        changed = []
        for indicator in indicators:
            bar = self.indexDailyBarDao.getByDate(indexCode, indicator.trade_date)
            if bar is None:
                continue
            maxPoint = max(maxPoint, bar.close)

            print("maxPoint", maxPoint, indicator.trade_date)
            if maxPoint > 0 and not indicator.max_point:
                indicator.max_point = maxPoint
                changed.append(indicator)
                count += 1

        if count > 0:
            self.indexPrimaryIndicatorDao.bulkSave(changed)
            print("[%s] %d max point updated" % (indexCode, count))

        return count


if __name__ == "__main__":
    manager = IndexMaxPointProcessor()
    manager.process('000001')


