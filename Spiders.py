# coding: utf-8
# from spider.CSIndexSpider import CSIndexSpider
from spider.v3.IndexBarSpider import IndexBarSpider
from spider.v3.IndexWeightsSpider import IndexWeightsSpider
from spider.v3.StockBalanceSheetSpider import StockBalanceSheetSpider
from spider.v3.StockDailyBarAdjustNoneSpider import StockDailyBarAdjustNoneSpider
from spider.v3.StockDailyBarAdjustPrevSpider import StockDailyBarAdjustPrevSpider
from spider.v3.StockIncomeStatementSpider import StockIncomeStatementSpider
from spider.v3.StockPrimaryFinanceIndicatorSpider import StockPrimaryFinanceIndicatorSpider
from spider.v3.StockTradingDerivativeIndicatorSpider import StockTradingDerivativeIndicatorSpider


'''
Download all index weights
'''
spider = IndexWeightsSpider()
spider.downloadAllIndexConstituents()


'''
Download all index bars
'''
spider = IndexBarSpider()
spider.downloadAllIndexBars()


'''
Download all stock bars with no adjustment
'''
spider = StockDailyBarAdjustNoneSpider()
spider.downloadAll()


'''
Download all stock bars with prev adjustment
'''
spider = StockDailyBarAdjustPrevSpider()
spider.downloadAll()


'''
Download Balance Sheet
'''
spider = StockBalanceSheetSpider()
spider.downloadAll()

'''
Download Income Statement
'''
spider = StockIncomeStatementSpider()
spider.downloadAll()

'''
Download Primary Finance Indicator
'''
spider = StockPrimaryFinanceIndicatorSpider()
spider.downloadAll()

'''
Download Trading Derivative Indicator
'''
spider = StockTradingDerivativeIndicatorSpider()
spider.downloadAll()


