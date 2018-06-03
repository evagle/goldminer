# coding: utf-8
from datetime import datetime, timedelta, date

from evaluation.IndexConstituentManager import IndexConstituentManager
from evaluation.StockManager import StockManager
from models.models import IndexPrimaryIndicator
from storage.IndexConstituentDao import IndexConstituentDao
from storage.IndexPrimaryIndicatorDao import IndexPrimaryIndicatorDao
from storage.IndexesDao import IndexesDao
from storage.StockDao import StockDao


class IndexPEPBBaseProcessor:
    def __init__(self):
        self.indexConstituentManager = IndexConstituentManager()
        self.stockManager = StockManager()
        self.indexPrimaryIndicatorDao = IndexPrimaryIndicatorDao()
        self.indexDao = IndexesDao()
        self.indexConstituentDao = IndexConstituentDao()
        self.fieldName = None

    def getStartDate(self, code):
        if self.fieldName is None:
            raise Exception("Field name is not given.")
        d = self.indexPrimaryIndicatorDao.getLatestDate(code, self.fieldName)
        if d is None:
            d = self.indexDao.getIndexPublishDate(code)

        # recalculate from last constituent date
        latestDate = self.indexConstituentDao.getLatestDate(code)
        if latestDate is not None and latestDate < d:
            d = latestDate

        # stock data starts from 2005-01-04
        if d < date(2005, 1, 4):
            d = date(2015, 1, 4)

        return d

    def process(self, indexCode):
        pass
