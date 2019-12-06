# coding: utf-8
from datetime import date, datetime, timedelta

from goldminer.common.Utils import Utils
from goldminer.common.logger import get_logger
from goldminer.indicators.BaseIndicatorProcessor import BaseIndicatorProcessor
from goldminer.indicators.StockManager import StockManager
from goldminer.models.models import StockCustomIndicator
from goldminer.storage.DerivativeFinanceIndicatorDao import DerivativeFinanceIndicatorDao
from goldminer.storage.StockCustomIndicatorDao import StockCustomIndicatorDao
from goldminer.storage.StockDao import StockDao

logger = get_logger(__name__)


class ROERankProcessor(BaseIndicatorProcessor):
    """
    Calculate roe score according to roeavg(扣除非经常性损益后的平均净资产收益率)
    ROEAVG=扣非净利润/归属母公司的平均股东权益合计（期初期末平均）＊100%
    因为ROE是随着季度增长的，应该取相同季度的ROE比较才有意义

    1. 最近三年年报ROEAVG加权值
        a) 最近三年年报权重依次为1.0, 0.8, 0.6
        b) 公式为(w1*x1+w2*x2+w3*x3)/(w1+w2+w3)
        特殊情况处理
        i) 如果不足三年，则去掉对于分子分母，例如两年的公式为(w1*x1+w2*x2)/(w1+w2)

    """
    YEAR_WEIGHTS = [1, 0.8, 0.6]

    def __init__(self):
        self.stockDao = StockDao()
        self.derivativeFinanceDao = DerivativeFinanceIndicatorDao()
        self.stockCustomIndicatorDao = StockCustomIndicatorDao()

        self.derivativeFinanceIndicatorModels = self.prepareROEAVG()
        self.stocks = self.stockDao.getStockList()
        self.pubDates = self.stockDao.getAllStockPublishDate()

    def prepareROEAVG(self):
        dic = {}
        models = self.derivativeFinanceDao.getAllROEAVG()
        for model in models:
            if model.code not in dic:
                dic[model.code] = []
            dic[model.code].append(model)

        # 财报时间排序
        for code in dic:
            dic[code] = sorted(dic[code], key=lambda model: model.end_date, reverse=True)

        return dic

    def getLast3Year(self, models, endDate):
        """
        Given sorted derivative finance indicators of one code, return latest 3 year indicators with ROEAVG
        :param models: derivative finance indicators of one code
        :return: latest 3 year indicators has ROEAVG
        """
        result = []
        for model in models:
            if model.ROEAVG is not None and model.end_date.month == 12 and \
                    model.end_date <= endDate and model.pub_date <= endDate:
                result.append(model)
                if len(result) == 3:
                    return result

        return result

    def growth2Score(self, growth):
        """
        Growth rate in percent, for example, 0.3 for 30% grow
        :param growth: growth in percent
        :return: score
        """
        return float(growth)
        # return 1 / (1 + math.exp(-float(growth) / 10 * 2))

    def generateROEScore(self, quarterModels, yearModels):
        if len(yearModels) < 1:
            return None

        # year score
        yearScore = 0
        sumWeight = 0
        for i in range(min(3, len(yearModels))):
            yearScore += self.YEAR_WEIGHTS[i] * self.growth2Score(yearModels[i].ROEAVG)
            sumWeight += self.YEAR_WEIGHTS[i]
            print(yearModels[i].end_date, yearModels[i].ROEAVG,yearScore)

        print(yearScore/sumWeight)
        return yearScore / sumWeight

    def process(self, code, **kwargs):
        """
        Calculate roe score for stock by the end of `date`

        ## 中途调用bulksave会导致getLast2Quarter运行缓慢，debug发现在执行getLast2Quarter时出现了sql相关调用,
         原因是expire_on_commit=true导致每次提交数据就expire了
        :param code:
        :param kwargs: args `date` for end date of finance indicator
        :return: float roe score, 0 for no score based on finance indicators
        """
        if code not in self.derivativeFinanceIndicatorModels:
            logger.warn("No data found for code {}, return 0".format(code))
            return 0

        models = self.derivativeFinanceIndicatorModels[code]
        endDate = self.get_args(kwargs, 'date')
        yearModels = self.getLast3Year(models, endDate)
        score = self.generateROEScore(None, yearModels)
        if score is not None:
            return score
        return 0

    def processByDate(self, targetDate: date = None):
        stocks = self.stocks
        scores = []
        if targetDate is None:
            targetDate = datetime.today().date()

        logger.info("Start to process roe score/rank for date {}".format(targetDate))
        for code in stocks:
            if code not in self.pubDates:
                continue

            pubDate = self.pubDates[code]
            if pubDate > targetDate:
                continue

            score = self.process(code, date=targetDate)
            scores.append((code, score))

        scores = sorted(scores, key=lambda x: x[1], reverse=True)

        modelsInDB = self.stockCustomIndicatorDao.getAllAtDate(targetDate)

        updatedModels = []
        for i in range(len(scores)):
            code, score = scores[i]
            # rank = 100 - i * 100 / len(scores)
            key = (code, targetDate)
            if key in modelsInDB:
                model = modelsInDB[key]
            else:
                model = StockCustomIndicator()
                model.code = code
                model.trade_date = targetDate

            model.roe_score = Utils.formatFloat(score, 6)
            # model.roe_rank = Utils.formatFloat(rank, 6)
            updatedModels.append(model)

        logger.info("{} roe score/rank updated".format(len(updatedModels)))
        self.stockCustomIndicatorDao.bulkSave(updatedModels)
        logger.info("End of roe score/rank for date {}".format(targetDate))
        return updatedModels

    def processByDateRange(self, startDate, endDate):
        logger.info("Start range {} to {}".format(startDate, endDate))
        stockManager = StockManager()
        date = startDate
        while date <= endDate:
            if stockManager.isTradeDate(date):
                self.processByDate(date)
            date += timedelta(days=1)
        logger.info("End range {} to {}".format(startDate, endDate))

    def processAll(self):
        lastDate = self.stockCustomIndicatorDao.getLatestDate(code='000001', columnName='roe_score')
        startDate = lastDate + timedelta(days=1)
        endDate = datetime.today().date()
        self.processByDateRange(startDate, endDate)


if __name__ == "__main__":
    processor = ROERankProcessor()

    # processor.processByDate(targetDate=date(2019, 10, 28))
    processor.processAll()
    # processor.process('300012', date=date(2019, 10, 28))
