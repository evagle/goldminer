# coding: utf-8
import json
import urllib.request
from datetime import datetime
from urllib.error import HTTPError

import xlrd

from goldminer.common import GMConsts
from goldminer.common.Utils import Utils
from goldminer.models.models import IndexConstituent
from goldminer.storage.IndexConstituentDao import IndexConstituentDao
from goldminer.storage.IndexesDao import IndexesDao

'''
从cnindex下载最新的constituent数据，更新时间和更新日期不靠谱，经常出错
'''
class CnIndexSpider:
    CNINDEX_CONSTITUENT_URL = "http://www.cnindex.com.cn/docs/yb_%s.xls"

    def __init__(self):
        self.constituentsDao = IndexConstituentDao()
        self.indexesDao = IndexesDao()

    def fetchConstituentByCode(self, code):
        url = self.CNINDEX_CONSTITUENT_URL % code
        try:
            response = urllib.request.urlopen(url)
            content = response.read()
        except HTTPError:
            print("Fail to download file HTTPError: ", url)
            return None
        except TimeoutError:
            print("Fail to download file TimeoutError: ", url)
            return None
        else:
            if content is None or content == "":
                return None
            else:
                workbook = xlrd.open_workbook(file_contents = content)
                # sheet_names = workbook
                sheet = workbook.sheet_by_index(0)
                cols = sheet.col_values(2)

                if '证券代码' in cols:
                    cols.remove('证券代码')
                elif '样本股代码' in cols:
                    cols.remove('样本股代码')

                tradeDate = None
                today = datetime.now().date()
                if sheet.col_values(4)[0] == "":
                    tradeDate = sheet.col_values(5)[0]
                else:
                    tradeDate = sheet.col_values(7)[0]

                if tradeDate and (tradeDate.startswith("更新时间") or tradeDate.startswith("更新日期")):
                    try:
                        tradeDate = datetime.strptime(tradeDate[5:], "%Y-%m-%d").date()
                    except Exception as e:
                        print("[%s] Wrong update date format: %s" % (code, tradeDate))

                if tradeDate is None:
                    print("[%s] Failed to parse update date or date is wrong: %s" % (code, tradeDate))
                    tradeDate = today

                return [tradeDate, cols]

    def isCnIndex(self, code):
        model = self.indexesDao.getByCode(code)
        return model.source == GMConsts.CN_INDEX

    def checkAndUpdateLatestConstituents(self, code):
        if not self.isCnIndex(code):
            print("[%s] not CnIndex index" % code)
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
                model.source = GMConsts.CN_INDEX
                self.constituentsDao.add(model)
                print("[%s] no last found. Add first one, %s" % (code, model))
        elif not Utils.isListEqual(newConstituents, json.loads(last.constituents)):
            # 如果已经存在比当前还要新的数据，说明国政公司的tradeDate填错了，用今天的日期作为指数更新日期
            if last.trade_date > tradeDate:
                today = datetime.now().date()
                print("[%s] CN Index give a wrong trade date: %s, change to %s" % (code, tradeDate, today))
                tradeDate = today

            model = self.constituentsDao.getByDate(code, tradeDate)
            if model is None:
                model = IndexConstituent()
            model.code = code
            model.constituents = json.dumps(newConstituents)
            model.trade_date = tradeDate
            model.source = GMConsts.CN_INDEX
            self.constituentsDao.add(model)
            print("[%s] new constituents date = %s" % (code, model.trade_date))
            print(model)

        else:
            print("[%s] constituent is up to date." % code)

    def checkAndUpdateAllLatestConstituents(self):
        indexes = self.indexesDao.getIndexList()
        for code in indexes:
            if self.isCnIndex(code):
                self.checkAndUpdateLatestConstituents(code)
                # time.sleep(1)


if __name__ == "__main__":
    spider = CnIndexSpider()
    spider.checkAndUpdateAllLatestConstituents()
