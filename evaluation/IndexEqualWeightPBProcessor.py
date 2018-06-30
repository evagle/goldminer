# coding: utf-8
from datetime import datetime, timedelta, date
from decimal import Decimal

from common.Utils import Utils
from evaluation.IndexPEPBBaseProcessor import IndexPEPBBaseProcessor
from models.models import IndexPrimaryIndicator


class IndexEqualWeightPBProcessor(IndexPEPBBaseProcessor):
    def __init__(self):
        super(IndexEqualWeightPBProcessor, self).__init__()
        self.fieldName = "equal_weight_pb"

    def process(self, indexCode):
        d = self.getStartDate(indexCode)
        if d is None:
            print("[Error] Invalid start date, code = ", indexCode)
            return

        now = datetime.now().date()
        models = []
        print("[%s] calcEqualWeightedPB from %s to %s " % (indexCode, d, now))
        while d <= now:
            if self.stockManager.isTradeDate(d):
                model = self.indexPrimaryIndicatorDao.getByDate(indexCode, d)
                if model is None:
                    model = IndexPrimaryIndicator()
                    model.code = indexCode
                    model.trade_date = d

                constituents = self.indexConstituentManager.getConstituents(indexCode, d)
                if constituents is not None:
                    stockPB = [self.stockManager.getStockPB(stock, d) for stock in constituents]
                    pbsum = sum([1 / p if p > 0 else 0 for p in stockPB])
                    if pbsum == 0:
                        print("ERROR empty stock pb", indexCode, d, constituents)
                    if pbsum > 0:
                        pb = Utils.formatFloat(len(stockPB) / pbsum, 6)
                        model.equal_weight_pb = pb
                        models.append(model)
                else:
                    print("No constituent", indexCode, d)
            d = d + timedelta(days=1)

        print("[%s] Save %d equal weight pb" % (indexCode, len(models)))
        self.indexPrimaryIndicatorDao.bulkSave(models)

        return models


if __name__ == "__main__":
    manager = IndexEqualWeightPBProcessor()
    manager.process('000913')


