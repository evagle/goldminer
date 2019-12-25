# coding: utf-8
from time import time

from goldminer.indicators.IndexEqualWeightPBProcessor import IndexEqualWeightPBProcessor
from goldminer.indicators.IndexEqualWeightPEProcessor import IndexEqualWeightPEProcessor
from goldminer.indicators.IndexMedianPBProcessor import IndexMedianPBProcessor
from goldminer.indicators.IndexMedianPEProcessor import IndexMedianPEProcessor
from goldminer.indicators.IndexPEPBGradeProcessor import IndexPEPBGradeProcessor
from goldminer.indicators.IndexPEPBHeightProcessor import IndexPEPBHeightProcessor
from goldminer.indicators.IndexWeightedPBProcessor import IndexWeightedPBProcessor
from goldminer.indicators.IndexWeightedPEProcessor import IndexWeightedPEProcessor
from goldminer.storage.IndexPrimaryIndicatorDao import IndexPrimaryIndicatorDao
from goldminer.storage.IndexesDao import IndexesDao


class IndexPEPBGenerator:
    def __init__(self):
        self.indexDao = IndexesDao()
        self.indexPrimaryIndicatorDao = IndexPrimaryIndicatorDao()

        self.equalWeightPEProcessor = IndexEqualWeightPEProcessor()
        self.weightedPEProcessor = IndexWeightedPEProcessor()
        self.medianPEProcessor = IndexMedianPEProcessor()
        self.equalWeightPBProcessor = IndexEqualWeightPBProcessor()
        self.weightedPBProcessor = IndexWeightedPBProcessor()
        self.medianPBProcessor = IndexMedianPBProcessor()
        self.heightProcessor = IndexPEPBHeightProcessor()
        self.gradeProcessor = IndexPEPBGradeProcessor()
        self.__ticks = []

    def _tick(self, string):
        self.__ticks.append([time(), string])

    def _print_ticks(self):
        for i in range(1, len(self.__ticks)):
            tick = self.__ticks[i]
            print(tick[i][1], tick[i][0] - tick[i - 1][0])

    def execOneIndex(self, code):
        indexPrimaryIndicatorDict = self.indexPrimaryIndicatorDao.getByCodeDict(code)

        self._tick("start")
        self.equalWeightPEProcessor.process(code, indexPrimaryIndicatorDict)
        self._tick("equalWeightPEProcessor cost(s) = ")
        self.weightedPEProcessor.process(code, indexPrimaryIndicatorDict)
        self._tick("weightedPEProcessor cost(s) = ")
        self.medianPEProcessor.process(code, indexPrimaryIndicatorDict)
        self._tick("medianPEProcessor cost(s) = ")
        self.equalWeightPBProcessor.process(code, indexPrimaryIndicatorDict)
        self._tick("equalWeightPBProcessor cost(s) = ")
        self.weightedPBProcessor.process(code, indexPrimaryIndicatorDict)
        self._tick("weightedPBProcessor cost(s) = ")
        self.medianPBProcessor.process(code, indexPrimaryIndicatorDict)
        self._tick("medianPBProcessor cost(s) = ")

        self.heightProcessor.buildAllHeightIndicators(code)
        self._tick("heightProcessor cost(s) = ")

        self.gradeProcessor.buildAllGradeIndicators(code)
        self._tick("gradeProcessor cost(s) = ")

    def updateAll(self):
        indexes = self.indexDao.getImportantIndexList()
        for code in indexes:
            self.execOneIndex(code)

    def updateImportant(self):
        codes = [
            "399102",
            "399006",
            "000925",
            "000016",
            "399550",
            "000300",
            "000905",
            "000804",
            "000015",
            "000922",
            "399321",
            "399324",
            "000037",
            "000841",
            "000913",
            "000933",
            "000978",
            "000991",
            "399394",
            "399618",
            "000036",
            "000932",
            "000990",
            "000912",
            "000827",
            "399812",
            "000993",
            "399967",
            "399971",
            "399005",
            "399101"
        ]
        for code in codes:
            self.execOneIndex(code)


if __name__ == "__main__":
    peManager = IndexPEPBGenerator()
    peManager.updateAll()
