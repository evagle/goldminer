# coding: utf-8
from datetime import datetime, timedelta

from common import GMConsts
from common.Utils import Utils
from evaluation.IndexPEPBBaseProcessor import IndexPEPBBaseProcessor
from models.models import IndexPrimaryIndicator


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
                    stockCount = len(stockPETTM)
                    stockPETTM = Utils.iqrFilter(stockPETTM)

                    peSum = sum([1 / p if p > 0 else 0 for p in stockPETTM])
                    if peSum == 0:
                        print("ERROR empty stock pe", indexCode, d, constituents)
                        pe = GMConsts.ABNORMAL_MAX_PE
                    else:
                        pe = Utils.formatFloat(stockCount / peSum, 6)

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


