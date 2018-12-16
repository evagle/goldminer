# coding: utf-8
from datetime import date

from goldminer.indicators.IndexConstituentManager import IndexConstituentManager
from goldminer.indicators.StockManager import StockManager
from goldminer.storage.IndexConstituentDao import IndexConstituentDao
from goldminer.storage.IndexDailyBarDao import IndexDailyBarDao
from goldminer.storage.IndexPrimaryIndicatorDao import IndexPrimaryIndicatorDao
from goldminer.storage.IndexesDao import IndexesDao


class BaseIndicatorProcessor:
    def process(self, indexCode):
        pass
