# coding: utf-8
import json
import time
import urllib.request
from datetime import datetime
from urllib.error import HTTPError

import xlrd

from common.Utils import Utils
from models.models import IndexConstituent
from storage.IndexConstituentDao import IndexConstituentDao
from storage.IndexesDao import IndexesDao


class CSIndexSpider:
    CSINDEX_CONSTITUENT_URL = "http://www.csindex.cn/uploads/file/autofile/cons/%scons.xls"

    def __init__(self):
        self.constituentsDao = IndexConstituentDao()
        self.indexesDao = IndexesDao()

    def fetchConstituentByCode(self, code):
        url = self.CSINDEX_CONSTITUENT_URL % code
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
                workbook = xlrd.open_workbook(file_contents = content)
                # sheet_names = workbook
                sheet = workbook.sheet_by_index(0)
                cols = sheet.col_values(4)
                cols.remove('成分券代码Constituent Code')
                tradeDate = sheet.col_values(0)[1]
                return [tradeDate, cols]

    def isCSIndex(self, code):
        model = self.indexesDao.getByCode(code)
        return model.pub_organization == "中证指数有限公司"

    def checkAndUpdateLatestConstituents(self, code):
        if code[0:2] != "00" and not self.isCSIndex(code):
            print("[%s] not CSIndex index" % code)
            return

        result = self.fetchConstituentByCode(code)
        if result is None:
            print("[%s] no new constituent found")
            return

        tradeDate = result[0]
        newConstituents = result[1]

        today = datetime.now().date()
        last = self.constituentsDao.getConstituents(code, today)
        if last is None:
            if len(newConstituents) == 0:
                print("[%s] has no constituent found" % code)
            else:
                model = IndexConstituent()
                model.code = code
                model.constituents = json.dumps(newConstituents)
                model.trade_date = tradeDate
                self.constituentsDao.add(model)
                print("[%s] not last found. Add first one, %s" % (code, model))
        elif not Utils.isListEqual(newConstituents, json.loads(last.constituents)):
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
            if code[0:2] == "00":
                self.checkAndUpdateLatestConstituents(code)
                time.sleep(1)


if __name__ == "__main__":
    spider = CSIndexSpider()
    spider.checkAndUpdateLatestConstituents('399001')
