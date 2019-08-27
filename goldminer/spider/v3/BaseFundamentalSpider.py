# coding: utf-8
from datetime import timedelta, datetime
import time

from goldminer.common.Utils import Utils
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

    def getCurrentModels(self, codes):
        modelsInDB = self.fundamentalsDao.getBatch(codes, self.modelClass)
        modelsDict = {}
        latestDateDict = {}
        for model in modelsInDB:
            key = model.code + model.end_date.strftime("%Y%m%d")
            modelsDict[key] = model
            if model.code not in latestDateDict:
                latestDateDict[model.code] = model.end_date
            else:
                latestDateDict[model.code] = Utils.maxDate(model.end_date,  latestDateDict[model.code])

        return modelsDict, latestDateDict

    def groupCodesToTwoByEndDate(self, latestDateDict):
        """
        将codes按照latest end date分成两组，一组大于一年，一组小于一年
        :return:
        """
        today = datetime.now().date()
        oneYearBefore = today - timedelta(days=365)
        codesOneYearLatestDate = today
        codesMoreThanOneYearLatestDate = today
        codesOneYear = []
        codesMoreThanOneYear = []
        for code in latestDateDict:
            date = latestDateDict[code]
            if date < oneYearBefore:
                codesMoreThanOneYear.append(self.codeToStockSymbol(code))
                codesOneYearLatestDate = Utils.minDate(codesOneYearLatestDate, date)
            else:
                codesOneYear.append(self.codeToStockSymbol(code))
                codesMoreThanOneYearLatestDate = Utils.minDate(codesMoreThanOneYearLatestDate, date)

        print("****111", (codesOneYearLatestDate, codesOneYear))
        print("****222", (codesMoreThanOneYearLatestDate, codesMoreThanOneYear))
        return (codesOneYearLatestDate, codesOneYear), (codesMoreThanOneYearLatestDate, codesMoreThanOneYear)

    def removeExists(self, currentModelsDict, models):
        """

        :param currentModelsDict: key : code + end_date.strftime("%Y%m%d"), value : model
        :param models:
        :return:
        """
        result = []
        for model in models:
            key = model.code + model.end_date.strftime("%Y%m%d")
            if key not in currentModelsDict:
                result.append(model)
        return result

    def downloadByCode(self, codes):
        if type(codes) == str:
            codes = [codes]

        endDate = datetime.now() + timedelta(days=1)
        modelName = self.getModelClassName()

        currentModelsDict, latestDateDict = self.getCurrentModels(codes)
        models = None
        for startDate, codes in self.groupCodesToTwoByEndDate(latestDateDict):
            symbols = [self.codeToStockSymbol(code) for code in codes]

            if startDate >= datetime.now().date():
                print("[%s\t%s] is up to date" % (codes, modelName))
                return None
            print("[%s\t%s] from %s to %s" % (modelName, codes, startDate, endDate))

            results = self.getFundamentals(table=self.table, symbols=symbols, start_date=startDate, end_date=endDate,
                                         limit=10000, fields=self.fields)

            models = [self.rawDataToModel(item) for item in results]
            try:
                models = self.removeExists(currentModelsDict, models)
                self.fundamentalsDao.addAll(models)
            except IntegrityError as e:
                print("[ERROR] failed to save %s, error message = %s " % (modelName, e))
                print("==data==", models)

            print("[%s\t%s] count = %d\n" % (modelName, codes, len(models)))

        return models

    def downloadAll(self):
        stocks = self.stockDao.getStockList()
        batch_size = 100
        while len(stocks) > 0:
            batch = stocks[:batch_size]
            stocks = stocks[batch_size:]
            result = self.downloadByCode(batch)
            if result is not None:
                time.sleep(0.1)

