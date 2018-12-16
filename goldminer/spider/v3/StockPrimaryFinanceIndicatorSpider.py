# coding: utf-8

from goldminer.models import PrimaryFinanceIndicator
from goldminer.spider.v3.BaseFundamentalSpider import BaseFundamentalSpider


class StockPrimaryFinanceIndicatorSpider(BaseFundamentalSpider):

    def __init__(self):
        super(StockPrimaryFinanceIndicatorSpider, self).__init__()
        self.modelClass = PrimaryFinanceIndicator
        self.table = 'prim_finance_indicator'
        self.fields = 'EBIT,EBITDA,EBITDASCOVER,EBITSCOVER,EPSBASIC,EPSBASICEPSCUT,EPSDILUTED,EPSDILUTEDCUT,EPSFULLDILUTED,EPSFULLDILUTEDCUT,EPSWEIGHTED,EPSWEIGHTEDCUT,NPCUT,OPNCFPS,ROEDILUTED,ROEDILUTEDCUT,ROEWEIGHTED,ROEWEIGHTEDCUT'


if __name__ == "__main__":
    spider = StockPrimaryFinanceIndicatorSpider()
    spider.downloadByCode('000001')
