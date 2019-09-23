# coding: utf-8

from goldminer.indicators.IndexEqualWeightPBProcessor import IndexEqualWeightPBProcessor
from goldminer.indicators.IndexEqualWeightPEProcessor import IndexEqualWeightPEProcessor
from goldminer.indicators.IndexMedianPBProcessor import IndexMedianPBProcessor
from goldminer.indicators.IndexMedianPEProcessor import IndexMedianPEProcessor
from goldminer.indicators.IndexPEPBGradeProcessor import IndexPEPBGradeProcessor
from goldminer.indicators.IndexPEPBHeightProcessor import IndexPEPBHeightProcessor
from goldminer.indicators.IndexWeightedPBProcessor import IndexWeightedPBProcessor
from goldminer.indicators.IndexWeightedPEProcessor import IndexWeightedPEProcessor
from goldminer.storage.IndexesDao import IndexesDao


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

    def execOneIndex(self, code):
        self.equalWeightPEProcessor.process(code)
        self.weightedPEProcessor.process(code)
        self.medianPEProcessor.process(code)
        self.equalWeightPBProcessor.process(code)
        self.weightedPBProcessor.process(code)
        self.medianPBProcessor.process(code)

        self.heightProcessor.buildAllHeightIndicators(code)

        self.gradeProcessor.buildAllGradeIndicators(code)

    def updateAll(self):
        indexes = self.indexDao.getIndexList()
        for code in indexes:
            # 跳过申万指数，没有数据
            if code.startswith("8"):
                continue
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
        ]
        for code in codes:
            self.execOneIndex(code)


if __name__ == "__main__":
    peManager = IndexPEPBGenerator()
    # peManager.updateImportant()
    peManager.execOneIndex('399102')

