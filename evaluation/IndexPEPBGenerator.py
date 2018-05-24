# coding: utf-8
from datetime import datetime, timedelta, date

from evaluation.IndexConstituentManager import IndexConstituentManager
from evaluation.StockManager import StockManager
from models.models import IndexPrimaryIndicator
from storage.IndexPrimaryIndicatorDao import IndexPrimaryIndicatorDao
from storage.IndexesDao import IndexesDao
from storage.StockDao import StockDao


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
        d = startDate
        if startDate is None:
            d = self.indexDao.getIndexPublishDate(indexCode)
        # stock data starts from 2005-01-04
        if d < date(2005, 1, 4):
            d = date(2015, 1, 4)

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
                    pesum = sum([1 / p if p > 0 else 0 for p in stockPETTM])
                    if pesum == 0:
                        print("ERROR empty stock pe", indexCode, d, constituents)
                    if pesum > 0:
                        pe = len(stockPETTM) / pesum
                        model.equal_weight_pe = pe
                        models.append(model)
                else:
                    print("error", indexCode, d)
            d = d + timedelta(days=1)

        return models

    def updatePEByCode(self, code):
        now = datetime.now().date().strftime("%Y-%m-%d")
        d = self.indexPrimaryIndicatorDao.getLatestDate(code, "equal_weight_pe")
        if d is None:
            d = self.indexDao.getIndexPublishDate(code)

        print("[%s] (%s ~ %s) equal weight pe" % (code, d, now))
        models = self.calcEqualWeightedPE(code, d)
        print("[%s] Save %d equal weight pe" % (code, len(models)))
        self.indexPrimaryIndicatorDao.bulkSave(models)

    def updateAllPE(self):
        indexes = self.indexDao.getIndexList()
        for code in indexes:
            self.updatePEByCode(code)
            print(self.stockManager.stockPETTMNotFound)
            self.stockManager.stockPETTMNotFound = {}


if __name__ == "__main__":
    peManager = IndexPEPBGenerator()
    # models = peManager.calcEqualWeightedPE("000913", date(2018, 5, 10))
    peManager.updatePEByCode('000913')
    # peManager.updateAll()


