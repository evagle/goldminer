# coding: utf-8

import xlrd

from goldminer.common.Utils import Utils
from goldminer.common.logger import get_logger
from goldminer.spider.CSCNIndexBaseSpider import CSCNIndexBaseSpider

logger = get_logger(__name__)


class CSIndexSpider(CSCNIndexBaseSpider):

    def __init__(self):
        super(CSIndexSpider, self).__init__()
        self.url = "http://www.csindex.cn/uploads/file/autofile/cons/%scons.xls"

    def parseConstituent(self, xlsContent):
        if xlsContent is None:
            return None
        workbook = xlrd.open_workbook(file_contents=xlsContent)

        sheet = workbook.sheet_by_index(0)
        cols = sheet.col_values(4)
        cols.remove('成分券代码Constituent Code')
        tradeDate = Utils.parseConstituentUpdateDate(sheet.col_values(0)[1])
        return [tradeDate, cols]

    def isCorrectIndexType(self, code):
        model = self.indexesDao.getByCode(code)
        return code[0:2] == "00" or model.publisher == "中证公司"


if __name__ == "__main__":
    spider = CSIndexSpider()
    spider.checkAndUpdateAllLatestConstituents()
