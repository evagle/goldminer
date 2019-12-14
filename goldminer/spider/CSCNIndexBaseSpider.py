# coding: utf-8
import json
import time
import urllib.request
from abc import abstractmethod
from datetime import datetime
from urllib.error import HTTPError

from goldminer.common import GMConsts
from goldminer.common.Utils import Utils
from goldminer.common.logger import get_logger
from goldminer.models.models import IndexConstituent
from goldminer.storage.IndexConstituentDao import IndexConstituentDao
from goldminer.storage.IndexesDao import IndexesDao

logger = get_logger(__name__)


class CSCNIndexBaseSpider:
    def __init__(self):
        self.constituentsDao = IndexConstituentDao()
        self.indexesDao = IndexesDao()
        self.url = None

    @abstractmethod
    def parseConstituent(self, xlsContent):
        pass

    @abstractmethod
    def isCorrectIndexType(self, code):
        pass

    def downloadXlsFile(self, code):
        url = self.url % code
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
                return content

    def checkAndUpdateLatestConstituents(self, code):
        """
        1. Fetch latest bar from database
            1.1 if None, insert the new one
            1.2 if latest.trade_date < new.trade_date,  insert the new one
            1.3 if latest.trade_date = new.trade_date, compare constituents and update

        :param code:
        :return:
        """
        if not self.isCorrectIndexType(code):
            logger.info("[{}] incorrect index type".format(code))
            return

        content = self.downloadXlsFile(code)
        if content is None:
            logger.info("[{}] download xls failed. url = {}".format(code, self.url % code))
            return

        result = self.parseConstituent(content)

        if result is None or len(result[1]) is None:
            logger.info("[{}] parse xls content failed or constituents empty".format(code))
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
            if self.isCorrectIndexType(code):
                self.checkAndUpdateLatestConstituents(code)
                time.sleep(0.1)
