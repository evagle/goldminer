# coding: utf-8
import math
from datetime import date, datetime, timedelta
from decimal import Decimal

from goldminer.common.Utils import Utils
from goldminer.common.logger import get_logger
from goldminer.indicators.BaseIndicatorProcessor import BaseIndicatorProcessor
from goldminer.indicators.StockManager import StockManager
from goldminer.models.models import StockCustomIndicator
from goldminer.storage.DerivativeFinanceIndicatorDao import DerivativeFinanceIndicatorDao
from goldminer.storage.StockCustomIndicatorDao import StockCustomIndicatorDao
from goldminer.storage.StockDao import StockDao

logger = get_logger(__name__)


class EPSRankProcessor(BaseIndicatorProcessor):
    """
    Calculate eps score according to net profit cut(扣除非经常性损益后的净利润) growth ratio
    1. 最近两个季度的扣非净利润增长率得分，权重1.0
        a) 上季度的扣非净利润增长率权重为1.0
        b) 上上季度扣非净利润增长率权重0.9
        c) 公式为(w1*x1+w2*x2)/(w1+w2)
        特殊情况处理
        i) 上季度报告没出来：暂时不考虑季报的公布时间的差异，每个公司按照能取到的最新两个季报数据做处理
        ii) 上季度报告就是上年年报：重合的情况会导致同一个数据在季报增速和年报增速计算两次，暂不考虑去重
        iii) 对于财报少于两个季度的公司直接排除，不参与计算
    2. 最近三年年报扣非净利润增长率得分，权重0.9
        a) 最近三年年报权重依次为1.0, 0.8, 0.6
        b) 公式为(w1*x1+w2*x2+w3*x3)/(w1+w2+w3)
        特殊情况处理
        i) 如果不足三年，则去掉对于分子分母，例如两年的公式为(w1*x1+w2*x2)/(w1+w2)

    """
    OVERALL_QUARTER_SCORE_WEIGHT = 1
    QUARTER_WEIGHTS = [1, 0.9]
    OVERALL_YEAR_SCORE_WEIGHT = 0.9
    YEAR_WEIGHTS = [1, 0.8, 0.6]

    def __init__(self):
        self.stockDao = StockDao()
        self.derivativeFinanceDao = DerivativeFinanceIndicatorDao()
        self.stockCustomIndicatorDao = StockCustomIndicatorDao()

        self.derivativeFinanceIndicatorModels = self.prepareNetProfitCutGrowth()
        self.stocks = self.stockDao.getStockList()
        self.pubDates = self.stockDao.getAllStockPublishDate()

    def prepareNetProfitCutGrowth(self):
        dic = {}
        models = self.derivativeFinanceDao.getAllNPCUT()
        for model in models:
            if model.code not in dic:
                dic[model.code] = []
            dic[model.code].append(model)

        # 财报时间排序
        for code in dic:
            dic[code] = sorted(dic[code], key=lambda model: model.end_date, reverse=True)
            dic[code] = list(filter(lambda model: model.NPCUT != 0, dic[code]))

        # 计算同比增速
        for code in dic:
            models = dic[code]
            n = len(models)
            for i in range(n):
                current = models[i]
                current.NPCUTGrowth = None
                for j in range(i + 1, n):
                    if self.isDiffOneYear(current.end_date, models[j].end_date):
                        current.NPCUTGrowth = float(
                            (current.NPCUT - models[j].NPCUT) / Decimal(math.fabs(models[j].NPCUT)))
                        if abs(current.NPCUTGrowth) > 10:
                            logger.warn("Imposible growth {}".format(current.NPCUTGrowth))
                            current.NPCUTGrowth = 10 if current.NPCUTGrowth > 0 else -10
                        break

        return dic

    def isDiffOneYear(self, date1: date, date2: date):
        return abs(date1.year - date2.year) == 1 and date1.month == date2.month and date1.day == date2.day

    def getLast2Quarter(self, models, endDate):
        """
        Given sorted derivative finance indicators of one code, return latest two indicators with NPCUTGrowth
        :param endDate: pub_date,end_date < endDate
        :param models: derivative finance indicators of one code
        :return: latest two indicators has NPCUTGrowth
        """
        result = []
        for model in models:
            if model.NPCUTGrowth is None:
                continue
            if model.end_date > endDate:
                continue
            if model.pub_date <= endDate:
                result.append(model)
                if len(result) == 2:
                    return result
        return result[:2]

    def getLast3Year(self, models, endDate):
        """
        Given sorted derivative finance indicators of one code, return latest 3 year indicators with NPCUTGrowth
        :param models: derivative finance indicators of one code
        :return: latest 3 year indicators has NPCUTGrowth
        """
        result = []
        for model in models:
            if model.NPCUTGrowth is not None and model.end_date.month == 12 and \
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
        return 1 / (1 + math.exp(-float(growth) * 10 / 1.3))

    def generateEPSScore(self, quarterModels, yearModels):
        # quater score
        if len(quarterModels) < 2:
            return None
        if len(yearModels) < 1:
            return None

        quarterScore = 0
        sumWeight = 0
        for i in range(2):
            quarterScore += EPSRankProcessor.QUARTER_WEIGHTS[i] * self.growth2Score(quarterModels[i].NPCUTGrowth)
            sumWeight += EPSRankProcessor.QUARTER_WEIGHTS[i]
            print("quarter", quarterModels[i].NPCUTGrowth, quarterScore)
        quarterScore /= sumWeight
        print("quarter22", quarterScore)
        # year score
        yearScore = 0
        for i in range(min(3, len(yearModels))):
            yearScore += EPSRankProcessor.YEAR_WEIGHTS[i] * self.growth2Score(yearModels[i].NPCUTGrowth)
            sumWeight += EPSRankProcessor.YEAR_WEIGHTS[i]
            print("year", yearModels[i].NPCUTGrowth, yearScore)
        yearScore /= sumWeight

        print("year22", yearScore)
        score = (EPSRankProcessor.OVERALL_QUARTER_SCORE_WEIGHT * quarterScore +
                 EPSRankProcessor.OVERALL_YEAR_SCORE_WEIGHT * yearScore) / \
                (EPSRankProcessor.OVERALL_QUARTER_SCORE_WEIGHT + EPSRankProcessor.OVERALL_YEAR_SCORE_WEIGHT)
        print(score)
        return score

    def process(self, code, **kwargs):
        """
        Calculate eps score for stock by the end of `date`

        ## 中途调用bulksave会导致getLast2Quarter运行缓慢，debug发现在执行getLast2Quarter时出现了sql相关调用
        原因是expire_on_commit=true导致每次提交数据就expire了
        :param code:
        :param kwargs: args `date` for end date of finance indicator
        :return: float eps score, 0 for no score based on finance indicators
        """
        if code not in self.derivativeFinanceIndicatorModels:
            logger.warn("No data found for code {}, return 0".format(code))
            return 0

        models = self.derivativeFinanceIndicatorModels[code]
        endDate = self.get_args(kwargs, 'date')
        quarterModels = self.getLast2Quarter(models, endDate)
        yearModels = self.getLast3Year(models, endDate)
        score = self.generateEPSScore(quarterModels, yearModels)
        if score is not None:
            return score
        return 0

    def process_by_date(self, target_date: date = None):
        stocks = self.stocks
        scores = []
        if target_date is None:
            target_date = datetime.today().date()

        logger.info("Start to process eps score/rank for date {}".format(target_date))
        for code in stocks:
            if code not in self.pubDates:
                continue

            pubDate = self.pubDates[code]
            if pubDate > target_date:
                continue

            score = self.process(code, date=target_date)
            scores.append((code, score))

        scores = sorted(scores, key=lambda x: x[1], reverse=True)

        modelsInDB = self.stockCustomIndicatorDao.getAllAtDate(target_date)

        updatedModels = []
        for i in range(len(scores)):
            code, score = scores[i]
            rank = 100 - i * 100 / len(scores)
            key = (code, target_date)
            if key in modelsInDB:
                model = modelsInDB[key]
            else:
                model = StockCustomIndicator()
                model.code = code
                model.trade_date = target_date

            model.eps_score = Utils.formatFloat(score, 6)
            model.eps_rank = Utils.formatFloat(rank, 6)
            updatedModels.append(model)

        logger.info("{} eps score/rank updated for date {}".format(len(updatedModels), target_date))
        self.stockCustomIndicatorDao.bulkSave(updatedModels)
        logger.info("End of eps score/rank for date {}".format(target_date))
        return updatedModels

    def processByDateRange(self, startDate, endDate):
        logger.info("Start range {} to {}".format(startDate, endDate))
        stockManager = StockManager()
        date = startDate
        while date <= endDate:
            if stockManager.isTradeDate(date):
                self.process_by_date(date)
            date += timedelta(days=1)
        logger.info("End range {} to {}".format(startDate, endDate))

    def processAll(self):
        lastDate = self.stockCustomIndicatorDao.getLatestDate(code='000001', columnName='eps_score')
        startDate = lastDate + timedelta(days=1)
        endDate = datetime.today().date()
        self.processByDateRange(startDate, endDate)


if __name__ == "__main__":
    processor = EPSRankProcessor()

    processor.processAll()
