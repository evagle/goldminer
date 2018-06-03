# coding: utf-8
from spider.CSIndexSpider import CSIndexSpider


'''
Download all index constituents
'''
spider = CSIndexSpider()
spider.checkAndUpdateAllLatestConstituents()


