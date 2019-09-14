# coding: utf-8
from datetime import date, timedelta, datetime

from goldminer.indicators.IndexConstituentManager import IndexConstituentManager
from goldminer.indicators.StockManager import StockManager
from goldminer.storage.IndexConstituentDao import IndexConstituentDao
from goldminer.storage.IndexDailyBarDao import IndexDailyBarDao
from goldminer.storage.IndexPrimaryIndicatorDao import IndexPrimaryIndicatorDao
from goldminer.storage.IndexesDao import IndexesDao


class IndexPEPBBaseProcessor:
    def __init__(self):
        self.indexConstituentManager = IndexConstituentManager()
        self.stockManager = StockManager()
        self.indexPrimaryIndicatorDao = IndexPrimaryIndicatorDao()
        self.indexDao = IndexesDao()
        self.indexConstituentDao = IndexConstituentDao()
        self.indexDailyBarDao = IndexDailyBarDao()
        self.fieldName = None

    def getStartDate(self, code):
        if self.fieldName is None:
            raise Exception("Field name is not given.")
        d = self.indexPrimaryIndicatorDao.getLatestDate(code, self.fieldName) + timedelta(days=1)
        if d is None:
            d = self.indexDao.getIndexPublishDate(code)

        # recalculate from last constituent date, but only when constituent update date is in 5 days,
        # otherwise it should already have been recalculated
        latestDate = self.indexConstituentDao.getLatestDate(code)
        if latestDate is not None and latestDate < d and (latestDate - datetime.today().date()).days < 5:
            d = latestDate

        # stock data starts from 2005-01-04
        if d < date(2005, 1, 4):
            d = date(2005, 1, 4)

        return d

    def process(self, indexCode):
        pass
