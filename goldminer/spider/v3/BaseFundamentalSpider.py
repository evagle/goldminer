# coding: utf-8
from datetime import timedelta, datetime
import time

from sqlalchemy.exc import IntegrityError

from goldminer.spider.v3.GMBaseSpiderV3 import GMBaseSpiderV3
from goldminer.storage import StockDao
from goldminer.storage import StockFundamentalsDao


class BaseFundamentalSpider(GMBaseSpiderV3):

    def __init__(self):
        super(BaseFundamentalSpider, self).__init__()
        self.fundamentalsDao = StockFundamentalsDao()
        self.stockDao = StockDao()

        '''
        Subclass has to provide modelClass, table and fields
        '''
        self.modelClass = None
        self.table = ''
        self.fields = ''

    def getModelClassName(self):
        return getattr(self.modelClass, '__name__')

    '''
    Override this function when have special requirements
    '''
    def rawDataToModel(self, code, rawBar):
        model = self._rawDataToModel(code, rawBar, self.modelClass)
        model.code = code
        model = self.fillWithZero(model)
        return model

    def fillWithZero(self, model):
        fields = self.fields.split(",")
        for field in fields:
            if hasattr(model, field) and getattr(model, field) is None:
                setattr(model, field, 0)
        return model

    def downloadByCode(self, code):
        startDate = self.fundamentalsDao.getLatestDate(code, self.modelClass) + timedelta(days=1)
        endDate = datetime.now() + timedelta(days=1)
        symbol = self.codeToStockSymbol(code)

        modelName = self.getModelClassName()
        if startDate >= datetime.now().date():
            print("[%s\t%s] is up to date" % (code, modelName))
            return None
        print("[%s\t%s] from %s to %s" % (modelName, code, startDate, endDate))

        results = self.getFundamentals(table=self.table, symbols=symbol, start_date=startDate, end_date=endDate,
                                     limit=10000, fields=self.fields)

        items = [self.rawDataToModel(code, item) for item in results]
        try:
            self.fundamentalsDao.addAll(items)
        except IntegrityError as e:
            print("[ERROR] failed to save %s, error message = %s " % (modelName, e))
            print("==data==", items)

        print("[%s\t%s] count = %d\n" % (modelName, code, len(items)))
        return items

    def downloadAll(self):
        stocks = self.stockDao.getStockList()
        for code in stocks:
            result = self.downloadByCode(code)
            if result is not None:
                time.sleep(0.1)
