# coding: utf-8
from datetime import datetime, timedelta, date

from evaluation.IndexConstituentManager import IndexConstituentManager
from evaluation.StockManager import StockManager
from models.models import IndexPrimaryIndicator
from storage.IndexPrimaryIndicatorDao import IndexPrimaryIndicatorDao
from storage.IndexesDao import IndexesDao


class IndexPEPBGenerator:
    def __init__(self):
        self.indexConstituent = IndexConstituentManager()
        self.stockManager = StockManager()
        self.indexPrimaryIndicatorDao = IndexPrimaryIndicatorDao()
        self.indexDao = IndexesDao()

    def getProfitAt(self, indexCode, date):
        sql = "SELECT code, pub_date, end_date, NETPROFIT FROM income_statement WHERE code = '%s' and pub_date <= '%s' ORDER BY pub_date LIMIT 1"
        sql = sql % (indexCode, date.strftime("%Y-%m-%d"))
        result = self.db.executeSql(sql)
        if len(result) > 0:
            return {"code": result[0][0], "pub_date": result[0][1], "end_date": result[0][2],
                    "net_profit": result[0][3]}

    def getLatestDateOfField(self, indexCode, field):
        sql = "SELECT pub_date FROM index_derivative_indicator WHERE code = '%s' and %s is not null"
        sql = sql % (indexCode, field)
        result = self.db.executeSql(sql)
        if len(result) == 0:
            return datetime(2005, 1, 4)
        else:
            return result[0][0]

    def calcEqualWeightedPE(self, indexCode, startDate = None):
        d = date(2005, 1, 4) if startDate is None else startDate
        now = datetime.now().date()

        models = []
        print(d, now)
        while d <= now:
            if self.stockManager.isTradeDate(d):
                model = self.indexPrimaryIndicatorDao.getByDate(indexCode, d)
                if model is None:
                    model = IndexPrimaryIndicator()
                    model.code = indexCode
                    model.trade_date = d

                constituents = self.indexConstituent.getConstituents(indexCode, d)
                if constituents is not None:
                    stockPETTM = [self.stockManager.getStockPETTM(stock, d) for stock in constituents]
                    pe = len(stockPETTM) / sum([1 / p if p > 0 else 0 for p in stockPETTM])
                    model.equal_weight_pe = pe
                    models.append(model)
                else:
                    print("error", indexCode, d)
            d = d + timedelta(days=1)

        return models

    def updateAllByCode(self, code):
        now = datetime.now().date().strftime("%Y-%m-%d")
        d = self.indexPrimaryIndicatorDao.getLatestDate(code, "equal_weight_pe")
        print("[%s] (%s - %s) equal weight pe" % (code, d.strftime("%Y-%m-%d"), now))
        models = self.calcEqualWeightedPE(code, d)
        print("[%s] Save %s equal weight pe" % (len(models), code))
        self.indexPrimaryIndicatorDao.bulkSave(models)

    def updateAll(self):
        indexes = self.indexDao.getIndexList()
        for code in indexes:
            self.updateAllByCode(code)


if __name__ == "__main__":
    peManager = IndexPEPBGenerator()
    # models = peManager.calcEqualWeightedPE("000913", date(2018, 5, 10))
    # peManager.updateAllByCode('000913')
    peManager.updateAll()


