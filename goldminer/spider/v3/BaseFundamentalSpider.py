# coding: utf-8
from datetime import timedelta, datetime
import time

from goldminer.common import GMConsts

from goldminer.common.Utils import Utils
from sqlalchemy.exc import IntegrityError

from goldminer.common.logger import get_logger
from goldminer.spider.v3.GMBaseSpiderV3 import GMBaseSpiderV3
from goldminer.storage.StockDao import StockDao
from goldminer.storage.StockFundamentalsDao import StockFundamentalsDao

logger = get_logger(__name__)

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

    def downloadByCodes(self, codes):
        if type(codes) == str:
            codes = [codes]

        startDate = datetime.now().date()
        endDate = datetime.now() + timedelta(days=1)
        symbols = []
        for code in codes:
            d = self.fundamentalsDao.getLatestDate(code, self.modelClass) + timedelta(days=1)
            startDate = Utils.minDate(startDate, d)
            symbols.append(code)

        modelName = self.getModelClassName()
        if startDate >= datetime.now().date():
            logger.info("[%s] %s is up to date" % (codes, modelName))
            return None
        logger.info("[%s] %s from %s to %s" % (modelName, codes, startDate, endDate))

        results = self.getFundamentals(table=self.table, symbols=symbols, start_date=startDate, end_date=endDate,
                                       limit=10000, fields=self.fields)
        items = [self.rawDataToModel(item) for item in results]

        try:
            self.fundamentalsDao.addAll(items)
        except IntegrityError as e:
            logger.error("[ERROR] failed to save %s, error message = %s " % (modelName, e))

        logger.info("[%s] %s count = %d\n" % (modelName, codes, len(items)))
        return items

    def downloadAll(self, batch_size=GMConsts.GET_FUNDAMENTAL_BATCH_SIZE):
        stocks = self.stockDao.getStockList(includeB=True)
        for i in range(int(len(stocks)/batch_size+1)):
            codes = stocks[i*batch_size:(i+1)*batch_size]
            result = self.downloadByCodes(codes)
            if result is not None:
                time.sleep(0.1)