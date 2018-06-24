# coding: utf-8
import json
import math
from datetime import timedelta, datetime
from decimal import Decimal

from evaluation.IndexPEPBBaseProcessor import IndexPEPBBaseProcessor


class IndexPBGradeTenYearProcessor(IndexPEPBBaseProcessor):

    def __init__(self):
        super(IndexPBGradeTenYearProcessor, self).__init__()
        self.fieldName = "pb_grade_ten_year"

    def process(self, indexCode):
        indicators = self.indexPrimaryIndicatorDao.getByCode(indexCode)
        if len(indicators) == 0:
            print("[%s] no data found." % indexCode)
            return

        changed = []
        for current in indicators:
            if current.pb_grade_ten_year is not None:
                continue
            tenYearBefore = current.trade_date - timedelta(days=3650)
            pbs = []
            for i in indicators:
                if tenYearBefore <= i.trade_date < current.trade_date:
                    pbs.append(i.equal_weight_pb)

            if len(pbs) == 0:
                continue

            # 统计10年pb的10%，30%，80%，100%对应的pb值
            pbs = sorted(pbs)
            n = len(pbs)

            grades = [float(pbs[min(int(n*p), n-1)].quantize(Decimal('0.0'))) for p in [0.1, 0.3, 0.8, 1]]

            current.pb_grade_ten_year = json.dumps(grades)
            print("[%s] %s trade_date = %s, grades = %s"% (indexCode, self.fieldName, current.trade_date, current.pb_grade_ten_year))
            changed.append(current)

        if len(changed) > 0:
            self.indexPrimaryIndicatorDao.bulkSave(changed)
            print("[%s] %d %s updated" % (indexCode, len(changed), self.fieldName))

        return 0


if __name__ == "__main__":
    manager = IndexPBGradeTenYearProcessor()
    manager.process('000001')

