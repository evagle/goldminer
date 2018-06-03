# coding: utf-8
from datetime import datetime, timedelta, date

from common.Utils import Utils
from evaluation.IndexPEPBBaseProcessor import IndexPEPBBaseProcessor
from models.models import IndexPrimaryIndicator


class IndexMedianPBProcessor(IndexPEPBBaseProcessor):

    def __init__(self):
        super(IndexMedianPBProcessor, self).__init__()
        self.fieldName = "median_pb"

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
                    pbs = [p for p in stockPB if p > 0]
                    pbs.sort()
                    if len(pbs) == 0:
                        print("ERROR empty stock pb", indexCode, d, constituents)
                    else:
                        pb = Utils.getMedian(pbs)
                        model.median_pb = pb
                        models.append(model)
                else:
                    print("No constituent", indexCode, d)
            d = d + timedelta(days=1)

        print("[%s] Save %d median weight pb" % (indexCode, len(models)))
        self.indexPrimaryIndicatorDao.bulkSave(models)

        return models


if __name__ == "__main__":
    manager = IndexMedianPBProcessor()
    manager.process('000913')


