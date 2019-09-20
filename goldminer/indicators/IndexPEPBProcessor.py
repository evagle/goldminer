# coding: utf-8
from abc import abstractmethod
from datetime import datetime, timedelta

from goldminer.common.logger import get_logger
from goldminer.indicators.IndexPEPBBaseProcessor import IndexPEPBBaseProcessor
from goldminer.models.models import IndexPrimaryIndicator, TradingDerivativeIndicator
from goldminer.storage.TradingDerivativeIndicatorDao import TradingDerivativeIndicatorDao

logger = get_logger(__name__)


class IndexPEPBProcessor(IndexPEPBBaseProcessor):
    def __init__(self):
        super(IndexPEPBProcessor, self).__init__()
        self.fieldName = "equal_weight_pb"
        self.tradingDerivativeDao = TradingDerivativeIndicatorDao()

    def getPrimaryIndicator(self, indexCode, d, primaryIndicatorDict):
        if (indexCode, d) in primaryIndicatorDict:
            model = primaryIndicatorDict[indexCode, d]
        else:
            model = IndexPrimaryIndicator()
            model.code = indexCode
            model.trade_date = d
        return model

    @abstractmethod
    def calculatePEPBIndicator(self, pepbList, **params):
        pass

    def calcIndicatorByDate(self, indexCode, d, primaryIndicatorDict):
        logger.info("[{}] started code={}, date={}".format(self.fieldName, indexCode, d))
        model = self.getPrimaryIndicator(indexCode, d, primaryIndicatorDict)

        constituents = self.indexConstituentManager.getConstituents(indexCode, d)
        if constituents is None:
            logger.warn("No constituent found for code {} date {}".format(indexCode, d))
            return None

        if self.fieldName in ["equal_weight_pb", "weighted_pb", "median_pb"]:
            column = TradingDerivativeIndicator.PB
        else:
            column = TradingDerivativeIndicator.PETTM

        pepbDict = self.tradingDerivativeDao.getColumnValuesByDate(d, column)
        totalMarketValueDict = None
        if self.fieldName in ["weighted_pe", "weighted_pb"]:
            totalMarketValueDict = self.tradingDerivativeDao.getColumnValuesByDate(d,
                                                                                   TradingDerivativeIndicator.TOTMKTCAP)

        filteredPEPB = []
        for stock in constituents:
            if stock in pepbDict:
                filteredPEPB.append(pepbDict[stock])

        if len(filteredPEPB) == 0:
            logger.warn(
                "[{}] code {} date {} has no PB/PETTM found, constituents={}".format(self.fieldName, indexCode, d,
                                                                                     constituents))
            return None

        indicatorVal = self.calculatePEPBIndicator(filteredPEPB, indexCode=indexCode, date=d, constituents=constituents,
                                                   pepbDict=pepbDict, totalMarketValueDict=totalMarketValueDict)
        if indicatorVal is not None:
            setattr(model, self.fieldName, indicatorVal)
            logger.info("[{}] new indicator value code={}, date={}, value={}".format(self.fieldName, indexCode, d,
                                                                                     indicatorVal))
            return model
        else:
            return None

    def process(self, indexCode):
        d = self.getStartDate(indexCode)
        if d is None:
            logger.error("[{}] Invalid start date, code = {}".format(self.fieldName, indexCode))
            return

        now = datetime.now().date()
        models = []
        logger.info("[{}] Start {} from {} to {} ".format(self.fieldName, indexCode, d, now))
        primaryIndicatorDict = self.indexPrimaryIndicatorDao.getByCodeDict(indexCode)
        while d <= now:
            if self.stockManager.isTradeDate(d):
                model = self.calcIndicatorByDate(indexCode, d, primaryIndicatorDict)
                if model:
                    models.append(model)
            d = d + timedelta(days=1)

        logger.info("[{}] {} values updated".format(self.fieldName, len(models)))
        self.indexPrimaryIndicatorDao.bulkSave(models)
        logger.info("[{}]  End {}".format(self.fieldName, indexCode))

        return models
