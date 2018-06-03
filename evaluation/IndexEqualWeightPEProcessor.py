# coding: utf-8
from datetime import datetime, timedelta, date

from evaluation.IndexConstituentManager import IndexConstituentManager
from evaluation.IndexPEPBBaseProcessor import IndexPEPBBaseProcessor
from evaluation.StockManager import StockManager
from models.models import IndexPrimaryIndicator
from storage.IndexConstituentDao import IndexConstituentDao
from storage.IndexPrimaryIndicatorDao import IndexPrimaryIndicatorDao
from storage.IndexesDao import IndexesDao
from storage.StockDao import StockDao


class IndexEqualWeightPEProcessor(IndexPEPBBaseProcessor):
    def __init__(self):
        super(IndexEqualWeightPEProcessor, self).__init__()
        self.fieldName = "equal_weight_pe"

    def process(self, indexCode):
        d = self.getStartDate(indexCode)
        if d is None:
            print("[Error] Invalid start date, code = ", indexCode)
            return

        now = datetime.now().date()
        models = []
        print("[%s] calcEqualWeightedPE from %s to %s " % (indexCode, d, now))
        while d <= now:
            if self.stockManager.isTradeDate(d):
                model = self.indexPrimaryIndicatorDao.getByDate(indexCode, d)
                if model is None:
                    model = IndexPrimaryIndicator()
                    model.code = indexCode
                    model.trade_date = d

                constituents = self.indexConstituentManager.getConstituents(indexCode, d)
                if constituents is not None:
                    stockPETTM = [self.stockManager.getStockPETTM(stock, d) for stock in constituents]
                    pesum = sum([1 / p if p > 0 else 0 for p in stockPETTM])
                    if pesum == 0:
                        print("ERROR empty stock pe", indexCode, d, constituents)
                    if pesum > 0:
                        pe = len(stockPETTM) / pesum
                        model.equal_weight_pe = pe
                        models.append(model)
                else:
                    print("No constituent", indexCode, d)
            d = d + timedelta(days=1)

        print("[%s] Save %d equal weight pe" % (indexCode, len(models)))
        self.indexPrimaryIndicatorDao.bulkSave(models)

        return models


if __name__ == "__main__":
    peManager = IndexEqualWeightPEProcessor()
    peManager.process('000001')


