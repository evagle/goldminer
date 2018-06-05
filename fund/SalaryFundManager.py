# coding: utf-8
from datetime import timedelta, datetime

from evaluation.StockManager import StockManager
from fund.FundSpider import FundSpider
from models.models import FundDailyBar, SalaryFund, SalaryFundDeal
from storage.FundDailyBarDao import FundDailyBarDao
from storage.SalaryFundDao import SalaryFundDao
from storage.SalaryFundDealDao import SalaryFundDealDao


class SalaryFundManager:
    def __init__(self):
        self.fundDailyBarDao = FundDailyBarDao()
        self.dealDao = SalaryFundDealDao()
        self.salaryFundDao = SalaryFundDao()
        self.stockManager = StockManager()

    # 获取指定日期的fund信息, 如果是周一，则上一个交易日的
    def getFundByDate(self, date) -> SalaryFund:
        model = self.salaryFundDao.getByDate(date)
        if model is None:
            raise Exception("Failed to get salary fund equal or before date : %s" % date)
        return model

    def getFundValueByDate(self, code, date):
        bar = self.fundDailyBarDao.getByDate(code, date)
        if bar is not None:
            return bar.net_asset_value
        else:
            raise Exception("Failed to get fund value, code = %s, date = %s" % (code, date))

    # 计算账户中的证券部分的价值
    # 将账户中下雨等于date的所有操作都计算进来，计算每一个基金的份额，乘以当前的基金净值，得到总的证券价值
    # 正常当天的价值需要在第二天才能计算，因为ETF等基金净值通常要晚上8，9点之后才会更新
    # 计算证券价值只需考虑买入和卖出基金的操作，现金注入和取出不用考虑
    def calcSecurityValue(self, date):

        # datestr = date.strftime("%Y-%m-%d")
        # sql = "SELECT code,share,trade_type from salary_fund_changes where trade_date <= '%s' order by trade_date" % datestr
        # result = self.db.executeSql(sql)
        deals = self.dealDao.getDealsBeforeDate(date)
        ## (('512580', 5200.0, 'buy'), ('512000', 5800.0, 'sell'))
        total_value = 0
        for deal in deals:
            if deal.trade_type == "buy":
                net_value = self.getFundValueByDate(deal.code, date)
                total_value += deal.share * net_value
            elif deal.trade_type == "sell":
                net_value = self.getFundValueByDate(deal.code, date)
                total_value -= deal.share * net_value
        return total_value

    # 购买基金，注入现金，取出现金会导致份额变化
    # 在前一天的净值和份额的基础上，加上当天的操作带来的这些份额变化
    def calcShares(self, date):
        prev_date = self.stockManager.getPreviousTradeDate(date)
        prev_fund = self.getFundByDate(prev_date)
        prev_net_value = prev_fund.net_value
        prev_share = prev_fund.share
        share = prev_share
        deals = self.dealDao.getByDate(date)
        for deal in deals:
            if deal.trade_type == "cashout" and deal.total_money > 0:
                deal.total_money = -deal.total_money
            if deal.trade_type in ["buy", "cashin", "cashout"]:
                share += deal.total_money / prev_net_value
        return share

    # 计算指定日期的cash剩余
    # 基金卖出，注入现金，取出现金会导致现金变化
    def calcCash(self, date):
        prev_date = self.stockManager.getPreviousTradeDate(date)
        prev_fund = self.getFundByDate(prev_date)
        prev_cash = prev_fund.cash
        cash = prev_cash
        deals = self.dealDao.getByDate(date)
        for deal in deals:
            if deal.trade_type == "cashout" and deal.total_money > 0:
                deal.total_money = -deal.total_money
            if deal.trade_type in ["sell", "cashin", "cashout"]:
                cash += deal.total_money
        return cash


    # 计算指定日期的基金份额
    # 在前一天的份额和净值的基础上，分三种情况更新份额：
    # - day2 买入一只基金，总共花去4000，手续费5元，当天的操作都不会计算到前一天净值里，等明天算今天的净值才要考虑
    # - day3 先按照day1净值买入4000基金，计算获得多少份额
    # - day3 计算day2的证券部分的价值
    # - day3 (证券价值+现金)/总份额 = day2净值
    #
    # - day6 取出现金x
    # - day7 按照day5的净值计算取出现金x的份额，减去该份额，减去现金x
    # - day7 计算day6的证券部分的价值
    # - day7 (证券价值+现金)/总份额 = day6净值
    #
    # * day8 注入现金y
    # * day9 按照day7的净值计算现金y的份额，加上份额，加上现金y
    # * day9 计算day8的证券部分的价值
    # * day9 (证券价值+现金)/总份额 = day8净值
    def updateFundByDate(self, date):
        if not self.stockManager.isTradeDate(date):
            raise Exception("Date %s is a invalid trade date" % date.strftime("%Y-%m-%d"))
        share = self.calcShares(date)
        security_assets = self.calcSecurityValue(date)
        cash = self.calcCash(date)
        total_money = security_assets + cash
        net_value = total_money / share

        fund = SalaryFund()
        fund.trade_date = date
        fund.total_assets = total_money
        fund.security_assets = security_assets
        fund.cash = cash
        fund.share = share
        fund.net_value = net_value
        self.salaryFundDao.add(fund)

        print(fund)

    # 更新salary fund，计算所有未计算的数据并插入数据库
    def updateAllFund(self):
        date = self.salaryFundDao.getLatestDate() + timedelta(days=1)
        end = datetime.now().date()
        print("Update salary fund from %s to %s" % (date, end))
        while date < end:
            if self.stockManager.isTradeDate(date):
                self.updateFundByDate(date)

            date = date + timedelta(days=1)


if __name__ == "__main__":
    spider = FundSpider()
    spider.updateAllFund()

    manager = SalaryFundManager()
    manager.updateAllFund()

