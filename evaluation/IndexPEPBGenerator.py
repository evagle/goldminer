# coding: utf-8

from evaluation.IndexEqualWeightPBProcessor import IndexEqualWeightPBProcessor
from evaluation.IndexEqualWeightPEProcessor import IndexEqualWeightPEProcessor
from evaluation.IndexMaxPbProcessor import IndexMaxPBProcessor
from evaluation.IndexMaxPeProcessor import IndexMaxPEProcessor
from evaluation.IndexMaxPointProcessor import IndexMaxPointProcessor
from evaluation.IndexMedianPBProcessor import IndexMedianPBProcessor
from evaluation.IndexMedianPEProcessor import IndexMedianPEProcessor
from evaluation.IndexPBGradeTenYearProcessor import IndexPBGradeTenYearProcessor
from evaluation.IndexPBHeightTenYearProcessor import IndexPBHeightTenYearProcessor
from evaluation.IndexPEGradeTenYearProcessor import IndexPEGradeTenYearProcessor
from evaluation.IndexPEHeightTenYearProcessor import IndexPEHeightTenYearProcessor
from evaluation.IndexWeightedPEProcessor import IndexWeightedPEProcessor
from storage.IndexesDao import IndexesDao


class IndexPEPBGenerator:
    def __init__(self):
        self.indexDao = IndexesDao()

        self.equalWeightPEProcessor = IndexEqualWeightPEProcessor()
        self.weightedPEProcessor = IndexWeightedPEProcessor()
        self.medianPEProcessor = IndexMedianPEProcessor()
        self.equalWeightPBProcessor = IndexEqualWeightPBProcessor()

        self.medianPBProcessor = IndexMedianPBProcessor()
        self.maxPEProcessor = IndexMaxPEProcessor()
        self.maxPBProcessor = IndexMaxPBProcessor()
        self.maxPointProcessor = IndexMaxPointProcessor()
        self.peHeightProcessor = IndexPEHeightTenYearProcessor()
        self.pbHeightProcessor = IndexPBHeightTenYearProcessor()
        self.peGradeProcessor = IndexPEGradeTenYearProcessor()
        self.pbGradeProcessor = IndexPBGradeTenYearProcessor()

    def updateAll(self):
        indexes = self.indexDao.getIndexList()
        for code in indexes:
            self.equalWeightPEProcessor.process(code)
            self.weightedPEProcessor.process(code)
            self.medianPEProcessor.process(code)
            self.equalWeightPBProcessor.process(code)
            self.medianPBProcessor.process(code)
            self.maxPEProcessor.process(code)
            self.maxPBProcessor.process(code)
            self.maxPointProcessor.process(code)
            self.peHeightProcessor.process(code)
            self.pbHeightProcessor.process(code)
            self.peGradeProcessor.process(code)
            self.pbGradeProcessor.process(code)


if __name__ == "__main__":
    peManager = IndexPEPBGenerator()
    peManager.updateAll()


