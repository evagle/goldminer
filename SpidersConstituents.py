# coding: utf-8
from spider.CSIndexSpider import CSIndexSpider
from spider.SzseSpider import SzseSpider

spider = CSIndexSpider()
spider.checkAndUpdateAllLatestConstituents()

spider = SzseSpider()
spider.checkAndUpdateAllLatestConstituents()

