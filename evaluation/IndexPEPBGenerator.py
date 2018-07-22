# coding: utf-8

from evaluation.IndexEqualWeightPBProcessor import IndexEqualWeightPBProcessor
from evaluation.IndexEqualWeightPEProcessor import IndexEqualWeightPEProcessor
from evaluation.IndexMedianPBProcessor import IndexMedianPBProcessor
from evaluation.IndexMedianPEProcessor import IndexMedianPEProcessor
from evaluation.IndexPEPBGradeProcessor import IndexPEPBGradeProcessor
from evaluation.IndexPEPBHeightProcessor import IndexPEPBHeightProcessor
from evaluation.IndexWeightedPBProcessor import IndexWeightedPBProcessor
from evaluation.IndexWeightedPEProcessor import IndexWeightedPEProcessor
from storage.IndexesDao import IndexesDao


class IndexPEPBGenerator:
    def __init__(self):
        self.indexDao = IndexesDao()

        self.equalWeightPEProcessor = IndexEqualWeightPEProcessor()
        self.weightedPEProcessor = IndexWeightedPEProcessor()
        self.medianPEProcessor = IndexMedianPEProcessor()
        self.equalWeightPBProcessor = IndexEqualWeightPBProcessor()
        self.weightedPBProcessor = IndexWeightedPBProcessor()
        self.medianPBProcessor = IndexMedianPBProcessor()
        self.heightProcessor = IndexPEPBHeightProcessor()
        self.gradeProcessor = IndexPEPBGradeProcessor()

    def execOneIndex(self,code):
        self.equalWeightPEProcessor.process(code)
        self.weightedPEProcessor.process(code)
        self.medianPEProcessor.process(code)
        self.equalWeightPBProcessor.process(code)
        self.weightedPBProcessor.process(code)
        self.medianPBProcessor.process(code)

        self.heightProcessor.runEqualWeightPEHeight()
        self.heightProcessor.process(code)

        self.heightProcessor.runEqualWeightPBHeight()
        self.heightProcessor.process(code)

        self.heightProcessor.runWeightedPEHeight()
        self.heightProcessor.process(code)

        self.heightProcessor.runWeightedPBHeight()
        self.heightProcessor.process(code)

        self.gradeProcessor.runEqualWeightPEGrade()
        self.gradeProcessor.process(code)

        self.gradeProcessor.runEqualWeightPBGrade()
        self.gradeProcessor.process(code)

        self.gradeProcessor.runWeightedPEGrade()
        self.gradeProcessor.process(code)

        self.gradeProcessor.runWeightedPBGrade()
        self.gradeProcessor.process(code)

    def updateAll(self):
        indexes = self.indexDao.getIndexList()
        for code in indexes:
            self.execOneIndex(code)

    def updateImportant(self):
        codes = [
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
        ]
        for code in codes:
            self.execOneIndex(code)


if __name__ == "__main__":
    peManager = IndexPEPBGenerator()
    peManager.updateImportant()


