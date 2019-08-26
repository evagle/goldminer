# coding: utf-8
from datetime import timedelta, datetime
import time

from sqlalchemy.exc import IntegrityError

from goldminer.spider.v3.GMBaseSpiderV3 import GMBaseSpiderV3
from goldminer.storage.StockDao import StockDao
from goldminer.storage.StockFundamentalsDao import StockFundamentalsDao


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
    def rawDataToModel(self, rawBar):
        model = self._rawDataToModel(rawBar, self.modelClass)
        symbol = 'symbol'
        if symbol in rawBar:
            model.code = self.symbolToCode(rawBar[symbol])

        model = self.fillWithZero(model)
        return model

    def fillWithZero(self, model):
        fields = self.fields.split(",")
        for field in fields:
            if hasattr(model, field) and getattr(model, field) is None:
                setattr(model, field, 0)
        return model

    def removeExists(self, codes, models):
        modelsInDB = self.fundamentalsDao.getBatch(codes, self.modelClass)
        modelsDict = {}
        for model in modelsInDB:
            key = model.code + model.pub_date.strftime("%Y%m%d")
            modelsDict[key] = model

        result = []
        for model in models:
            key = model.code + model.pub_date.strftime("%Y%m%d")
            if key not in modelsDict:
                result.append(model)
        return result

    def downloadByCode(self, codes):
        if type(codes) == str:
            codes = [codes]

        startDate = datetime.now().date()
        endDate = datetime.now() + timedelta(days=1)
        symbols = []
        for code in codes:
            date = self.fundamentalsDao.getLatestDate(code, self.modelClass) + timedelta(days=1)
            startDate = startDate if startDate <= date else date
            symbols.append(self.codeToStockSymbol(code))

        modelName = self.getModelClassName()
        if startDate >= datetime.now().date():
            print("[%s\t%s] is up to date" % (codes, modelName))
            return None
        print("[%s\t%s] from %s to %s" % (modelName, codes, startDate, endDate))

        results = self.getFundamentals(table=self.table, symbols=symbols, start_date=startDate, end_date=endDate,
                                     limit=10000, fields=self.fields)

        models = [self.rawDataToModel(item) for item in results]
        try:
            models = self.removeExists(codes, models)
            self.fundamentalsDao.addAll(models)
        except IntegrityError as e:
            print("[ERROR] failed to save %s, error message = %s " % (modelName, e))
            print("==data==", models)

        print("[%s\t%s] count = %d\n" % (modelName, codes, len(models)))
        return models

    def downloadAll(self):
        stocks = self.stockDao.getStockList()
        for code in stocks:
            result = self.downloadByCode(code)
            if result is not None:
                time.sleep(0.1)
