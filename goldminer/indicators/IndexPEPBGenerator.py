# coding: utf-8

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

    def execOneIndex(self, code):
        indexPrimaryIndicatorDict = self.indexPrimaryIndicatorDao.getByCodeDict(code)

        self.equalWeightPEProcessor.process(code, indexPrimaryIndicatorDict)
        self.weightedPEProcessor.process(code, indexPrimaryIndicatorDict)
        self.medianPEProcessor.process(code, indexPrimaryIndicatorDict)
        self.equalWeightPBProcessor.process(code, indexPrimaryIndicatorDict)
        self.weightedPBProcessor.process(code, indexPrimaryIndicatorDict)
        self.medianPBProcessor.process(code, indexPrimaryIndicatorDict)

        self.heightProcessor.buildAllHeightIndicators(code)

        self.gradeProcessor.buildAllGradeIndicators(code)

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
