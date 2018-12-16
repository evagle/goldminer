# coding: utf-8
from datetime import datetime
import json

from goldminer.common.Utils import Utils
from goldminer.models.models import IndexConstituent
from goldminer.storage.IndexConstituentDao import IndexConstituentDao


class RiceQuantImport:
    def __init__(self):
        self.indexConstituentDao = IndexConstituentDao()

    def importConstituents(self, filePath):
        fin = open(filePath, "r")
        line1 = fin.readline()
        line2 = fin.readline()
        while line1 and line1.strip() != "":
            args = line1.strip().split("\t")
            tradeDate = datetime.strptime(args[0], "%Y%m%d").date()
            code = args[1][0:6]
            constituents = []
            for i in json.loads(line2.strip()):
                constituents.append(i[0:6])
            print(tradeDate, code)
            old = self.indexConstituentDao.getByDate(code, tradeDate)
            last = self.indexConstituentDao.getConstituents(code, tradeDate)
            if old is None and (
                    last is None or
                    not Utils.isListEqual(constituents, json.loads(last.constituents))
            ):
                model = IndexConstituent()
                model.code = code
                model.trade_date = tradeDate
                model.constituents = json.dumps(constituents)
                self.indexConstituentDao.add(model)
                print("save*****", tradeDate, code)
            line1 = fin.readline()
            line2 = fin.readline()


if __name__ == "__main__":
    importer = RiceQuantImport()
    importer.importConstituents("/Users/abing/Downloads/index_components_all.csv")
