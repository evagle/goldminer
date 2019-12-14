# coding: utf-8
from datetime import datetime, timedelta
from decimal import Decimal
from math import fabs

import pandas as pd

from goldminer.common.logger import get_logger
from goldminer.models.models import Indexes
from goldminer.spider.tushare.TushareBase import TushareBase
from goldminer.spider.v3.IndexBarSpider import IndexBarSpider
from goldminer.storage.IndexesDao import IndexesDao

logger = get_logger(__name__)


class IndexSpider(TushareBase):
    def __init__(self):
        super(IndexSpider, self).__init__()
        self.indexDao = IndexesDao()
        self.exchangeMap = {"SSE": 1, "SZSE": 2}
        self.markets = {'MSCI': 'MSCI指数', 'CSI': '中证指数', 'SSE': '上交所指数', 'SZSE': '深交所指数', 'CICC': '中金所指数', 'SW': '申万指数'}

    def hasNoIndexConstituentData(self, code):
        return code in ["000013", "000022", "000023", "000140", "000170", "000188", "000834", "000836", "000837",
                        "000845", "000847", "000849", "000850", "000851", "000853", "000854", "000856", "000857",
                        "000858", "000863", "000865", "000867", "000869", "000923", "000924", "000999", "399110",
                        "399120", "399130", "399131", "399132", "399133", "399134", "399135", "399136", "399137",
                        "399138", "399139", "399140", "399150", "399160", "399170", "399180", "399190", "399200",
                        "399210", "399220", "399230", "399290", "399294", "399297", "399298", "399299", "399329",
                        "399902", "399906", "399921", "399923", "399924", "399940", "399955", "399981", "399984",
                        "399985", "000823", "000835", "000974", "399300", "399901", "399903", "399904", "399905",
                        "399907", "399913", "399914", "399915", "399916", "399918", "399920", "399926", "399927",
                        "399928", "399929", "399930", "399932", "399933", "399934", "399935", "399936", "399937",
                        "399938", "399941", "399942", "399943", "399944", "399945", "399946", "399947", "399948",
                        "399949", "399953", "399954", "399956", "399958", "399960", "399962", "399968", "399980",
                        "399982"]

    def _diff(self, indexA, indexB):
        fields = ["code", 'publisher', 'index_type', 'category', 'base_date', 'base_point', 'pub_date', 'weight_rule',
                  'description', 'end_date']
        changed = False
        for field in fields:
            if field == 'base_point':
                if fabs(getattr(indexA, field) - getattr(indexB, field)) > 1e-6:
                    changed = True
                    break
            elif getattr(indexA, field) != getattr(indexB, field):
                changed = True
                break
        if changed:
            for field in fields:
                setattr(indexA, field, getattr(indexB, field))
            return indexA
        else:
            return None

    def isExpired(self, code):
        """
        如果最近7天有daily bar则认为指数并未过期
        :param tsCode:
        :return:
        """
        today = datetime.today().date()
        date = today - timedelta(days=15)
        barSpider = IndexBarSpider()
        bars = barSpider.downloadBarsByDateRange(code, startDate=date, endDate=today, save=False)
        return len(bars) == 0

    def updateIndexListFromTushare(self):
        """
        从tushare下载所有指数列表，更新index数据库
        """
        logger.info("[IndexSpider] Start to update stock list")
        fields = ["ts_code",
                  "name",
                  "fullname",
                  "market",
                  "publisher",
                  "index_type",
                  "category",
                  "base_date",
                  "base_point",
                  "list_date",
                  "weight_rule",
                  "desc",
                  "exp_date"]

        currentIndexes = self.indexDao.all()
        currentIndexesDict = {}
        for model in currentIndexes:
            currentIndexesDict[model.code] = model

        newIndexes = {}
        for market in self.markets.keys():
            data = self.ts_pro_api.index_basic(market=market, fields=fields)
            logger.info("[IndexSpider] Get {} stocks from tushare market={}.".format(data.shape[0], market))
            for _, row in data.iterrows():
                code = row['ts_code'][:6]
                # 只保留0，3开头的指数
                if code[:1] not in ['0', '3', '8']:
                    continue

                if row['list_date'] is None:
                    continue

                if row['index_type'] is None:
                    continue

                if row['name'].find("新三板") >= 0:
                    continue

                index = Indexes()
                index.code = code
                index.name = row['name']
                index.index_type = row['index_type']
                index.category = row['category']
                index.full_name = row['fullname']
                index.pub_date = datetime.strptime(row['list_date'], '%Y%m%d').date()
                if row['base_date'] is not None:
                    index.base_date = datetime.strptime(row['base_date'], '%Y%m%d').date()

                # exp_date不准确，暂时不用
                # if row['exp_date'] is not None:
                #     isExpired = self.isExpired(code)
                #     if isExpired:
                #         index.end_date = datetime.strptime(row['exp_date'], '%Y%m%d').date()

                # 对于没有数据源的index标记为已过期
                if self.hasNoIndexConstituentData(code):
                    index.end_date = "1900-01-01"

                if pd.isna(row['base_point']):
                    index.base_point = 0
                else:
                    index.base_point = Decimal(round(row['base_point'], 2))
                index.weight_rule = row['weight_rule']
                index.publisher = row['publisher']
                # 错误数据修正
                if code in ['399701', '399702', '399703', '399704', '399705', '399706']:
                    index.publisher = "中证公司"

                index.description = row['desc']

                if code not in currentIndexesDict:
                    newIndexes[code] = index
                    logger.info("[IndexSpider] New index {}".format(index))
                else:
                    updatedStock = self._diff(currentIndexesDict[code], index)
                    if updatedStock:
                        newIndexes[code] = updatedStock
                        logger.info("[IndexSpider] Update index {}".format(updatedStock))

        self.indexDao.bulkSave(newIndexes.values())
        logger.info("[StockSpider] Save {} new indexes to db.".format(len(newIndexes)))


if __name__ == "__main__":
    spider = IndexSpider()
    spider.updateIndexListFromTushare()
