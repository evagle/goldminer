# coding: utf-8
import urllib.request
from urllib.error import HTTPError

import xlrd


class CSIndexSpider:
    CSINDEX_CONSTITUENT_URL = "http://www.csindex.cn/uploads/file/autofile/cons/%scons.xls"

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
                print(cols)



spider = CSIndexSpider()
spider.fetchConstituentByCode('000001')
