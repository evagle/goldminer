# coding: utf-8
import json
import math
from datetime import timedelta, datetime

from goldminer.common.Utils import Utils
from goldminer.indicators.IndexPEPBBaseProcessor import IndexPEPBBaseProcessor


class IndexPEPBGradeProcessor(IndexPEPBBaseProcessor):

    def __init__(self):
        super(IndexPEPBGradeProcessor, self).__init__()
        self.fieldName = None
        self.sourceFieldName = None

    def runEqualWeightPEGrade(self):
        self.fieldName = "ew_pe_grade_ten_year"
        self.sourceFieldName = "equal_weight_pe"

    def runEqualWeightPBGrade(self):
        self.fieldName = "ew_pb_grade_ten_year"
        self.sourceFieldName = "equal_weight_pb"

    def runWeightedPEGrade(self):
        self.fieldName = "w_pe_grade_ten_year"
        self.sourceFieldName = "weighted_pe"

    def runWeightedPBGrade(self):
        self.fieldName = "w_pb_grade_ten_year"
        self.sourceFieldName = "weighted_pb"

    def process(self, indexCode):
        indicators = self.indexPrimaryIndicatorDao.getByCode(indexCode)
        if len(indicators) == 0:
            print("[%s] PEPBGradeProcessor  no data found." % indexCode)
            return

        changed = []
        queue = []
        date_queue = []
        for current in indicators:
            if getattr(current, self.fieldName) is not None:
                continue

            val = getattr(current, self.sourceFieldName)
            if val is not None:
                queue.append(val)
                date_queue.append(current.trade_date)
                if (current.trade_date - date_queue[0]).days > 3650:
                    queue.pop(0)
                    date_queue.pop(0)

            pes = queue.copy()

            if len(pes) == 0:
                continue

            # 统计10年pe的10%，30%，80%，100%对应的pe值
            pes = sorted(pes)
            n = len(pes)

            grades = [pes[min(int(n*p), n-1)] for p in [0.1, 0.3, 0.8, 1]]
            grades = [Utils.formatFloat(i, 1) for i in grades]
            gradesJson = json.dumps(grades)
            setattr(current, self.fieldName, gradesJson)
            print("[%s] %s trade_date = %s, grades = %s"% (indexCode, self.fieldName, current.trade_date, gradesJson))
            changed.append(current)

        if len(changed) > 0:
            self.indexPrimaryIndicatorDao.bulkSave(changed)
            print("[%s] %d %s updated" % (indexCode, len(changed), self.fieldName))

        return 0


if __name__ == "__main__":
    manager = IndexPEPBGradeProcessor()
    manager.runWeightedPBGrade()
    manager.process('399001')



