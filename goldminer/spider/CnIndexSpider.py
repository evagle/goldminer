# coding: utf-8

import re

import xlrd

from goldminer.common.Utils import Utils
from goldminer.common.logger import get_logger
from goldminer.spider.CSCNIndexBaseSpider import CSCNIndexBaseSpider

logger = get_logger(__name__)


class CnIndexSpider(CSCNIndexBaseSpider):
    """
    从cnindex下载最新的constituent数据，更新时间和更新日期不靠谱，经常出错
    """
    def __init__(self):
        super(CnIndexSpider, self).__init__()
        self.url = "http://www.cnindex.com.cn/docs/yb_%s.xls"

    def parseConstituent(self, xlsContent):
        if xlsContent is None:
            return None
        workbook = xlrd.open_workbook(file_contents=xlsContent)

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
                tradeDate = Utils.parseConstituentUpdateDate(sheet.row(1)[i].value)
            elif columnName.startswith("更新时间") or columnName.startswith("更新日期"):
                result = re.match(r".*([\d]{4}-[\d]{1,2}-[\d]{1,2}).*", columnName)
                if len(result.groups()) > 0:
                    tradeDate = Utils.parseConstituentUpdateDate(result.groups()[0])

        if cols is None or tradeDate is None:
            return None

        if '证券代码' in cols:
            cols.remove('证券代码')
        elif '样本股代码' in cols:
            cols.remove('样本股代码')

        return [tradeDate, cols]

    def isCorrectIndexType(self, code):
        model = self.indexesDao.getByCode(code)
        return model.publisher == "深交所"


if __name__ == "__main__":
    spider = CnIndexSpider()
    spider.checkAndUpdateAllLatestConstituents()
