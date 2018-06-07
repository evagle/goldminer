# coding: utf-8
from fund.FundSpider import FundSpider
from fund.SalaryFundManager import SalaryFundManager

spider = FundSpider()
spider.updateAllFund()

manager = SalaryFundManager()
manager.updateAllFund()