# coding: utf-8
import json

from spider.v3.GMBaseSpiderV3 import GMBaseSpiderV3
from storage.IndustryDao import IndustryDao
from storage.StockDao import StockDao

'''
从掘金的getIndustry接口下载stock的industy数据
tushare的数据质量太低
'''


class StockSpider(GMBaseSpiderV3):
    def __init__(self):
        super(StockSpider, self).__init__()
        self.stockDao = StockDao()
        self.industryDao = IndustryDao()

    def updateIndustry(self):
        industries = self.industryDao.all()
        for industry in industries:
            stocks = self.getIndustry(industry.code)
            for code in stocks:
                code = code[5:]
                stock = self.stockDao.getByCode(code)
                if stock:
                    if stock.industry is None or stock.industry == "":
                        stock.industry = []
                    else:
                        print(stock)
                        stock.industry = json.loads(stock.industry)

                    if industry.code not in stock.industry:
                        stock.industry.append(industry.code)
                        stock.industry = json.dumps(stock.industry)
                        self.stockDao.add(stock)
                        print("update industry: ", stock)


if __name__ == "__main__":
    spider = StockSpider()
    spider.updateIndustry()





