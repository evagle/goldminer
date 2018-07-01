# coding: utf-8
import math
from datetime import datetime, timedelta
from decimal import Decimal

from common import GMConsts
from common.Utils import Utils
from evaluation.IndexPEPBBaseProcessor import IndexPEPBBaseProcessor
from models.models import IndexPrimaryIndicator


class IndexWeightedPEProcessor(IndexPEPBBaseProcessor):

    def __init__(self):
        super(IndexWeightedPEProcessor, self).__init__()
        self.fieldName = "weighted_pe"

    def process(self, indexCode):
        d = self.getStartDate(indexCode)
        if d is None:
            print("[Error] Invalid start date, code = ", indexCode)
            return

        now = datetime.now().date()
        models = []
        print("[%s] calcWeightedPE from %s to %s " % (indexCode, d, now))
        while d <= now:
            if self.stockManager.isTradeDate(d):
                model = self.indexPrimaryIndicatorDao.getByDate(indexCode, d)
                if model is None:
                    model = IndexPrimaryIndicator()
                    model.code = indexCode
                    model.trade_date = d

                constituents = self.indexConstituentManager.getConstituents(indexCode, d)
                if constituents is not None:
                    profitSum = 0
                    totalMarketValueSum = 0
                    for stock in constituents:
                        pe = self.stockManager.getStockPETTM(stock, d)
                        value = self.stockManager.getStockTotalMarketValue(stock, d)

                        if value is None or value < 1 or math.fabs(pe) < 1e-6:
                            print("[ERROR] no pe, total market value for %s at date %s" % (stock, d))
                            continue

                        profit = value / Decimal(pe)
                        profitSum += profit
                        totalMarketValueSum += value

                    # 处理指数的利润异常的情况
                    # 1. 利润大于0，但是非常小，导致pe很大，限制pe为[0, GMConsts.ABNORMAL_MAX_PE]
                    # 2. 利润等于0，pe记录为GMConsts.ABNORMAL_MAX_PE
                    # 3. 利润小于0，pe记录为负数，限制范围[GMConsts.ABNORMAL_MIN_PE, 0]
                    if profitSum > 0:
                        pe = Utils.formatFloat(totalMarketValueSum / profitSum, 6)
                        pe = min(pe, GMConsts.ABNORMAL_MAX_PE)
                    elif profitSum == 0:
                        pe = GMConsts.ABNORMAL_MAX_PE
                    else:
                        pe = Utils.formatFloat(totalMarketValueSum / profitSum, 6)
                        pe = max(pe, GMConsts.ABNORMAL_MIN_PE)

                    model.weighted_pe = pe
                    models.append(model)
                    print("new weighted pe", indexCode, d, pe, profitSum, totalMarketValueSum)
                else:
                    print("No constituent", indexCode, d)
            d = d + timedelta(days=1)

        print("[%s] Save %d weighted pe" % (indexCode, len(models)))
        self.indexPrimaryIndicatorDao.bulkSave(models)

        return models


if __name__ == "__main__":
    peManager = IndexWeightedPEProcessor()
    peManager.process('000001')


