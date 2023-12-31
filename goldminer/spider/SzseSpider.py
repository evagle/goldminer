# coding: utf-8
import json
import time
import urllib.request
from datetime import datetime
from urllib.error import HTTPError

import xlrd

from goldminer.common.Utils import Utils
from goldminer.indicators.StockManager import StockManager
from goldminer.models.models import IndexConstituent
from goldminer.storage.IndexConstituentDao import IndexConstituentDao
from goldminer.storage.IndexesDao import IndexesDao


class SzseSpider:
    SZSE_CONSTITUENT_URL = "http://www.szse.cn/szseWeb/ShowReport.szse?SHOWTYPE=xlsx&CATALOGID=1747&ZSDM=%s&tab1PAGENO=1&ENCODE=1&TABKEY=tab1"

    def __init__(self):
        self.constituentsDao = IndexConstituentDao()
        self.indexesDao = IndexesDao()
        self.stockManager = StockManager()

    def fetchConstituentByCode(self, code):
        url = self.SZSE_CONSTITUENT_URL % code
        try:
            response = urllib.request.urlopen(url)
            content = response.read()
        except HTTPError:
            print("Fail to download file : ", url)
            return None
        else:
            if content is None or content == "":
                return None
            else:
                workbook = xlrd.open_workbook(file_contents=content)
                # sheet_names = workbook
                sheet = workbook.sheet_by_index(0)
                cols = sheet.col_values(0)
                cols.remove('证券代码')
                return cols

    def checkAndUpdateLatestConstituents(self, code):
        if code[0:2] != "39":
            print("[%s] not szse index" % code)
            return

        result = self.fetchConstituentByCode(code)
        if result is None:
            print("[%s] no new constituent found")
            return

        newConstituents = result

        today = datetime.now().date()
        last = self.constituentsDao.getConstituents(code, today)
        if last is None:
            if len(newConstituents) == 0:
                print("[%s] has no constituent found" % code)
            else:
                model = IndexConstituent()
                model.code = code
                model.constituents = json.dumps(newConstituents)
                model.trade_date = self.stockManager.getLastTradeDate()
                self.constituentsDao.add(model)
                print("[%s] not last found. Add first one, %s" % (code, model))

        elif not Utils.isListEqual(newConstituents, json.loads(last.constituents)):
            tradeDate = self.stockManager.getLastTradeDate()
            model = self.constituentsDao.getByDate(code, tradeDate)
            if model is None:
                model = IndexConstituent()
            model.code = code
            model.constituents = json.dumps(newConstituents)
            model.trade_date = tradeDate
            self.constituentsDao.add(model)
            print("[%s] new constituents date = %s" % (code, model.trade_date))
        else:
            print("[%s] constituent is up to date." % code)

    def checkAndUpdateAllLatestConstituents(self):
        indexes = self.indexesDao.getIndexList()
        for code in indexes:
            if code[0:2] == "39":
                self.checkAndUpdateLatestConstituents(code)
                time.sleep(1)


if __name__ == "__main__":
    spider = SzseSpider()
    spider.checkAndUpdateLatestConstituents('399001')
