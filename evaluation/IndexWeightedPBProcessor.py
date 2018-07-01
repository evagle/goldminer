# coding: utf-8
import math
from datetime import datetime, timedelta
from decimal import Decimal

from common.Utils import Utils
from evaluation.IndexPEPBBaseProcessor import IndexPEPBBaseProcessor
from models.models import IndexPrimaryIndicator


class IndexWeightedPBProcessor(IndexPEPBBaseProcessor):

    def __init__(self):
        super(IndexWeightedPBProcessor, self).__init__()
        self.fieldName = "weighted_pb"

    def process(self, indexCode):
        d = self.getStartDate(indexCode)
        if d is None:
            print("[Error] Invalid start date, code = ", indexCode)
            return

        now = datetime.now().date()
        models = []
        print("[%s] calcWeightedPB from %s to %s " % (indexCode, d, now))
        while d <= now:
            if self.stockManager.isTradeDate(d):
                model = self.indexPrimaryIndicatorDao.getByDate(indexCode, d)
                if model is None:
                    model = IndexPrimaryIndicator()
                    model.code = indexCode
                    model.trade_date = d

                constituents = self.indexConstituentManager.getConstituents(indexCode, d)
                if constituents is not None:
                    netAssetsSum = 0
                    totalMarketValueSum = 0
                    for stock in constituents:
                        pb = self.stockManager.getStockPB(stock, d)
                        value = self.stockManager.getStockTotalMarketValue(stock, d)

                        if value is None or value < 1 or math.fabs(pb) < 1e-6:
                            print("[ERROR] no pb, total market value for %s at date %s" % (stock, d))
                            continue
                        netAsset = value / Decimal(pb)
                        netAssetsSum += netAsset
                        totalMarketValueSum += value

                    if netAssetsSum > 0:
                        pb = Utils.formatFloat(totalMarketValueSum / netAssetsSum, 6)
                        model.weighted_pb = pb
                        models.append(model)
                        print("new weighted pb", indexCode, d, pb, netAssetsSum, totalMarketValueSum)
                    else:
                        print("[ERROR] weighted pb with net assets < 0")
                else:
                    print("No constituent", indexCode, d)
            d = d + timedelta(days=1)

        print("[%s] Save %d weighted pb" % (indexCode, len(models)))
        self.indexPrimaryIndicatorDao.bulkSave(models)

        return models


if __name__ == "__main__":
    peManager = IndexWeightedPBProcessor()
    peManager.process('000009')


