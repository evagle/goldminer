# coding: utf-8
from datetime import datetime, date
import json

from storage.IndexConstituentDao import IndexConstituentDao
from models.models import IndexConstituent

class RiceQuantImport:
    def __init__(self):
        self.indexConstituentDao = IndexConstituentDao()

    def importConstituents(self, filePath):
        fin = open(filePath, "r")
        line1 = fin.readline()
        line2 = fin.readline()
        while line1:
            args = line1.strip().split("\t")
            tradeDate = datetime.strptime(args[0], "%Y%m%d").date()
            code = args[1][0:6]
            constituents = []
            for i in json.loads(line2.strip()):
                constituents.append(i[0:6])
            print(tradeDate, code)
            model = IndexConstituent()
            model.code = code
            model.trade_date = tradeDate
            model.constituents = json.dumps(constituents)
            self.indexConstituentDao.add(model)
            line1 = fin.readline()
            line2 = fin.readline()



importer = RiceQuantImport()
importer.importConstituents("/Users/abing/Downloads/index_components_all.csv")
