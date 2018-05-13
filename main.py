# coding: utf-8
from spider.v3.IndexBarSpider import IndexBarSpider
from spider.v3.IndexConstituentsSpider import IndexConstituentsSpider
from spider.v3.StockBalanceSheetSpider import StockBalanceSheetSpider
from spider.v3.StockIncomeStatementSpider import StockIncomeStatementSpider
from spider.v3.StockPrimaryFinanceIndicatorSpider import StockPrimaryFinanceIndicatorSpider
from spider.v3.StockTradingDerivativeIndicatorSpider import StockTradingDerivativeIndicatorSpider

'''
Download all index constituents
'''
# spider = IndexConstituentsSpider()
# spider.downloadAllIndexConstituents()

'''
Download all index bars
'''
# spider = IndexBarSpider()
# spider.downloadAllIndexBars()

'''
Download Balance Sheet
'''
# spider = StockBalanceSheetSpider()
# spider.downloadAll()

'''
Download Income Statement
'''
# spider = StockIncomeStatementSpider()
# spider.downloadAll()

'''
Download Primary Finance Indicator
'''
# spider = StockPrimaryFinanceIndicatorSpider()
# spider.downloadAll()

'''
Download Trading Derivative Indicator
'''
spider = StockTradingDerivativeIndicatorSpider()
spider.downloadAll()


