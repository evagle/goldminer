# coding: utf-8
import json
import urllib.request
from datetime import datetime
from urllib.error import HTTPError

import xlrd
import re

from goldminer.common import GMConsts
from goldminer.common.Utils import Utils
from goldminer.models.models import IndexConstituent
from goldminer.storage.IndexConstituentDao import IndexConstituentDao
from goldminer.storage.IndexesDao import IndexesDao


class CnIndexSpider:
    """
    从cnindex下载最新的constituent数据，更新时间和更新日期不靠谱，经常出错
    """

    CNINDEX_CONSTITUENT_URL = "http://www.cnindex.com.cn/docs/yb_%s.xls"

    def __init__(self):
        self.constituentsDao = IndexConstituentDao()
        self.indexesDao = IndexesDao()

    def parseDate(self, datestr):
        if type(datestr) == float:
            tuple = xlrd.xldate_as_tuple(datestr, 0)
            return datetime(tuple[0], tuple[1], tuple[2])

        datestr = datestr.strip()
        if len(datestr) == 8 and datestr.find("-") < 0:
            format = "%Y%m%d"
        elif datestr.find("-") >= 0:
            parts = datestr.split("-")
            if len(parts) != 3:
                return None
            if len(parts[0]) != 4:
                return None
            format = "%Y-%m-%d"
        elif datestr.find("/") >= 0:
            parts = datestr.split("/")
            if len(parts) != 3:
                return None
            if len(parts[2]) != 4:
                return None
            format = "%m/%d/%Y"
        return datetime.strptime(datestr, format)

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
                workbook = xlrd.open_workbook(file_contents=content)
                # sheet_names = workbook
                sheet = workbook.sheet_by_index(0)

                headers = sheet.row(0)
                cols = None
                tradeDate = None
                for i in range(len(headers)):
                    cell = headers[i]
                    columnName = cell.value
                    if columnName.startswith("证券代码") or columnName.startswith("样本股代码"):
                        cols = sheet.col_values(i)
                    elif columnName.startswith("日期"):
                        tradeDate = self.parseDate(sheet.row(1)[i].value)
                    elif columnName.startswith("更新时间") or columnName.startswith("更新日期"):
                        result = re.match(r".*([\d]{4}-[\d]{1,2}-[\d]{1,2}).*", columnName)
                        if len(result.groups()) > 0:
                            tradeDate = self.parseDate(result.groups()[0])

                if cols is None or tradeDate is None:
                    raise Exception("[{}]Failed to extract constituents of tradedate from excel.".format(code))

                if '证券代码' in cols:
                    cols.remove('证券代码')
                elif '样本股代码' in cols:
                    cols.remove('样本股代码')

                return [tradeDate.date(), cols]

    def isCnIndex(self, code):
        model = self.indexesDao.getByCode(code)
        return model.source == GMConsts.CN_INDEX or model.publisher == "深交所"

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
            # 如果已经存在比当前还要新的数据，报错
            if last.trade_date > tradeDate:
                print("[%s] CN Index give a wrong trade date: %s, lastest trade_date found %s" % (
                code, tradeDate, last.trade_date))
                return

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
                try:
                    self.checkAndUpdateLatestConstituents(code)
                except Exception as e:
                    print("Failed to download constituent for code {}, error message={}".format(code, e))


if __name__ == "__main__":
    spider = CnIndexSpider()
    spider.checkAndUpdateLatestConstituents('399989')
