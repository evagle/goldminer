# coding: utf-8
import math
from datetime import date

from goldminer.indicators.BaseIndicatorProcessor import BaseIndicatorProcessor
from goldminer.storage.DerivativeFinanceIndicatorDao import DerivativeFinanceIndicatorDao


class EPSScoreProcessor(BaseIndicatorProcessor):
    """
    Calculate eps score according to net profit cut(扣除非经常性损益后的净利润) growth ratio
    1. 最近两个季度的扣非净利润增长率得分，权重1.0
        a) 上季度的扣非净利润增长率权重为1.0
        b) 上上季度扣非净利润增长率权重0.9
        特殊情况处理
        i) 上季度报告没出来：暂时不考虑季报的公布时间的差异，每个公司按照能取到的最新两个季报数据做处理
        ii) 上季度报告就是上年年报：重合的情况会导致同一个数据在季报增速和年报增速计算两次，暂不考虑去重
        iii) 对于财报少于两个季度的公司直接排除，不参与计算
    2. 最近三年年报扣非净利润增长率得分，权重0.9
        a) 最近三年年报权重依次为1.0, 0.8, 0.6

    """
    def __init__(self):
        self.derivativeFinanceDao = DerivativeFinanceIndicatorDao()
        self.derivativeFinanceIndicatorModels = self.prepareNetProfitCutGrowth()

    def prepareNetProfitCutGrowth(self):
        dic = {}
        models = self.derivativeFinanceDao.getByCode("000001")
        for model in models:
            if model.code not in dic:
                dic[model.code] = []
            dic[model.code].append(model)
        # 财报时间排序
        for code in dic:
            dic[code] = sorted(dic[code], key=lambda model: model.end_date, reverse=True)

        # 计算同比增速
        for code in dic:
            models = dic[code]
            n = len(models)
            for i in range(n):
                current = models[i]
                for j in range(i + 1, n):
                    if self.isDiffOneYear(current.end_date, models[j].end_date):
                        current.NPCUTGrowth = current.NPCUT / models[j].NPCUT - 1
                        break
        return dic

    def isDiffOneYear(self, date1:date, date2:date):
        return abs(date1.year - date2.year) == 1 and date1.month == date2.month and date1.day == date2.day

    def getLast2Quarter(self, models):
        """
        Given sorted derivative finance indicators of one code, return latest two indicators with NPCUTGrowth
        :param models: derivative finance indicators of one code
        :return: latest two indicators has NPCUTGrowth
        """
        models = models[:2]
        result = []
        for model in models:
            if hasattr(model, 'NPCUTGrowth'):
                result.append(model)
                print("getLast2Quater", model.end_date, model.NPCUTGrowth)

        return result

    def getLast3Year(self, models):
        """
        Given sorted derivative finance indicators of one code, return latest 3 year indicators with NPCUTGrowth
        :param models: derivative finance indicators of one code
        :return: latest 3 year indicators has NPCUTGrowth
        """
        result = []
        for model in models:
            if hasattr(model, 'NPCUTGrowth') and model.end_date.month == 12:
                result.append(model)
                print("getLast3Year", model.end_date, model.NPCUTGrowth)
        return result[:3]

    def growth2Score(self, growth):
        """
        Growth rate in percent, for example, 0.3 for 30% grow
        :param growth: growth in percent
        :return: score
        """
        return 1/(1+math.exp(growth*10))

    def generateEPSScore(self, quarterModels, YearModels):
        # quater score
        pass

        # year score
        


    def process(self, code, **kwargs):
        pass

if __name__ == "__main__":
    processor = EPSScoreProcessor()
    print("111", processor.getLast2Quarter(processor.derivativeFinanceIndicatorModels['000001']))

    print("222", processor.getLast3Year(processor.derivativeFinanceIndicatorModels['000001']))