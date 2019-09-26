# coding: utf-8
import json
import time
import urllib.request
from datetime import datetime
from urllib.error import HTTPError

import xlrd

from goldminer.common import GMConsts
from goldminer.common.Utils import Utils
from goldminer.common.logger import get_logger
from goldminer.models.models import IndexConstituent
from goldminer.storage.IndexConstituentDao import IndexConstituentDao
from goldminer.storage.IndexesDao import IndexesDao

logger = get_logger(__name__)


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
            logger.error("Fail to download file : {}".format(url))
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
                tradeDate = Utils.parseConstituentUpdateDate(sheet.col_values(0)[1])
                return [tradeDate, cols]

    def isCSIndex(self, code):
        model = self.indexesDao.getByCode(code)
        return model.source == GMConsts.CS_INDEX or code[0:2] == "00" or model.publisher == "中证公司"

    def checkAndUpdateLatestConstituents(self, code):
        """
        1. Fetch latest bar from database
            1.1 if None, insert the new one
            1.2 if latest.trade_date < new.trade_date,  insert the new one
            1.3 if latest.trade_date = new.trade_date, compare constituents and update

        :param code:
        :return:
        """
        if not self.isCSIndex(code):
            logger.info("[{}] not CSIndex index".format(code))
            return

        result = self.fetchConstituentByCode(code)

        if result is None or len(result[1]) is None:
            logger.info("[{}] no new constituent found".format(code))
            return
        if result[0] is None:
            logger.info("[{}] trade date is none.".format(code))
            return

        tradeDate = result[0]
        newConstituents = result[1]

        latest = self.constituentsDao.getConstituentsBeforeDate(code, datetime.today().date())
        if latest is None or latest.trade_date < tradeDate:
            model = IndexConstituent()
            model.code = code
            model.constituents = json.dumps(newConstituents)
            model.trade_date = tradeDate
            model.source = GMConsts.CS_INDEX
            self.constituentsDao.add(model)
            logger.info("[{}] insert new constituent {}".format(code, model))
        elif latest.trade_date == tradeDate:
            if not Utils.isListEqual(newConstituents, json.loads(latest.constituents)):
                latest.code = code
                latest.constituents = json.dumps(newConstituents)
                latest.trade_date = tradeDate
                latest.source = GMConsts.CS_INDEX
                self.constituentsDao.add(latest)
                logger.info("[{}] new constituents {}".format(code, latest))
            else:
                logger.info("[{}] constituent in database is up to date. trade date={}".format(code, tradeDate))
        else:
            logger.info("[{}] download an older constituents. trade date={}".format(code, tradeDate))

    def checkAndUpdateAllLatestConstituents(self):
        indexes = self.indexesDao.getIndexList()
        for code in indexes:
            if self.isCSIndex(code):
                self.checkAndUpdateLatestConstituents(code)
                time.sleep(0.1)


if __name__ == "__main__":
    spider = CSIndexSpider()
    spider.checkAndUpdateAllLatestConstituents()
