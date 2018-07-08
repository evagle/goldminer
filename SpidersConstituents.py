# coding: utf-8
from spider.CSIndexSpider import CSIndexSpider
from spider.CnIndexSpider import CnIndexSpider

spider = CSIndexSpider()
spider.checkAndUpdateAllLatestConstituents()

spider = CnIndexSpider()
spider.checkAndUpdateAllLatestConstituents()

