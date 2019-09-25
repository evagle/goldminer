# coding=utf-8
import json
import time
from datetime import timedelta, datetime

from goldminer.common.logger import get_logger
from goldminer.models.models import IndexWeight
from goldminer.spider.v3.GMBaseSpiderV3 import GMBaseSpiderV3
from goldminer.storage.IndexWeightDao import IndexWeightDao
from goldminer.storage.IndexesDao import IndexesDao

logger = get_logger(__name__)


class IndexWeightsSpider(GMBaseSpiderV3):

    def __init__(self):
        super(IndexWeightsSpider, self).__init__()
        self.indexWeightDao = IndexWeightDao()
        self.indexesDao = IndexesDao()

    def rawDataToModel(self, code, data) -> IndexWeight:
        model = IndexWeight()
        model.code = code
        model.trade_date = data['trade_date'].date()
        weights = data['constituents']
        if len(weights) == 1:
            logger.warn("Wrong weights data: code={}, data={}".format(code, data))
            return None

        weightsFormated = {}
        for k in weights:
            weightsFormated[k[5:]] = weights[k]

        model.constituents = json.dumps(weightsFormated)

        return model

    def downloadConstituents(self, code):
        startDate = self.indexWeightDao.getLatestDate(code) + timedelta(days=1)
        endDate = datetime.now() + timedelta(days=1)

        logger.info("[{}] Starts downloading weights from {} to {}".format(code, startDate, endDate))
        results = self.getHistoryConstituents(index=self.getIndexSymbol(code) + "." + code, start_date=startDate,
                                              end_date=endDate)

        models = []
        for item in results:
            if item['trade_date'].date() >= startDate:
                model = self.rawDataToModel(code, item)
                if model:
                    models.append(model)

        logger.info("[{}] End downloading weights, {} downloaded.".format(code, len(models)))
        self.indexWeightDao.addAll(models)
        return models

    def downloadAllIndexConstituents(self):
        if datetime.now().day < 25:
            logger.info("NO UPDATE: Index Weights from gm are published at the end of each month")
            return
        indexes = self.indexesDao.getIndexList()
        for code in indexes:
            self.downloadConstituents(code)
            time.sleep(0.1)


if __name__ == "__main__":
    spider = IndexWeightsSpider()
    spider.downloadAllIndexConstituents()
