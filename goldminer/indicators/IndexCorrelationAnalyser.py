# coding: utf-8

import numpy as np

from goldminer.storage.IndexCorrelationDao import IndexCorrelationDao
from goldminer.storage.IndexDailyBarDao import IndexDailyBarDao


class IndexCorrelationAnalyser:

    def __init__(self):
        self.indexDailyBarDao = IndexDailyBarDao()
        self.correlationDao = IndexCorrelationDao()

    def matchBarsByDate(self, barsA, barsB):

        # filter out bars with the same date
        result = {}
        datesA = sorted(barsA.keys())
        datesB = sorted(barsB.keys())
        for d in datesB:
            if d in datesA:
                result[d] = [barsA[d], barsB[d]]

        # get changes
        changes = [[], []]

        for key in result:
            item = result[key]
            # print(item)
            # t0 = time.time()
            if item[0]["pre_close"] > 0 and item[1]["pre_close"] > 0:
                # print(time.time()-t0)
                for i in [0, 1]:
                    changes[i].append((item[i]["close"] - item[i]["pre_close"]) / item[i]["pre_close"] * 100)

        return changes

    def calculateCorrelation(self, changes):
        return np.corrcoef(changes)[0][1]

    def corr(self, codeList):
        bars = {}
        firstDate = None
        for code in codeList:
            lst = self.indexDailyBarDao.getByCode(code)
            bars[code] = {}
            for bar in lst:
                d = bar.trade_date.strftime("%Y-%m-%d")
                bars[code][d] = bar.to_dict()

        for codeA in codeList:
            print(codeA)
            for codeB in codeList:
                changes = self.matchBarsByDate(bars[codeA], bars[codeB])
                correlation = self.calculateCorrelation(changes)
                model = self.correlationDao.getByCode(codeA, codeB)
                if not model:
                    model = IndexCorrelation()
                model.id = codeA + "_" + codeB
                model.codea = codeA
                model.codeb = codeB
                model.correlation = correlation
                self.correlationDao.add(model)

                print(codeA, codeB, correlation)


if __name__ == "__main__":
    analyser = IndexCorrelationAnalyser()
    analyser.corr(["000001", "399006", "399001", "399005", "000985", "000902", "000925", "000016",
                   "000300", "000905", "000804", "000015", "000922", "399321", "399324", "000037",
                   "000841", "000913", "000933", "000978", "000991", "399394", "399618", "000036",
                   "000932", "000990", "000912", "000827", "399812", "000993", "399967", "399971",
                   "000992"
                   ])
