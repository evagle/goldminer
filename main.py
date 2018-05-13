# coding: utf-8
from spider.v3.IndexBarSpider import IndexBarSpider
from spider.v3.IndexConstituentsSpider import IndexConstituentsSpider

'''
Download all index constituents
'''
# spider = IndexConstituentsSpider()
# spider.downloadAllIndexConstituents()

'''
Download all index bars
'''
spider = IndexBarSpider()
spider.downloadAllIndexBars()


