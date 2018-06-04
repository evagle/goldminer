# coding: utf-8

import sys
import time
from datetime import datetime, date

from fund.EastMoney import EastMoney
from models.models import FundDailyBar
from storage.FundDailyBarDao import FundDailyBarDao
from storage.SalaryFundDealDao import SalaryFundDealDao


class FundManager:
    def __init__(self):
        self.fundDailyBarDao = FundDailyBarDao()
        self.dealDao = SalaryFundDealDao()

    def downloadFundData(self, code, startdate):
        eastmoney = EastMoney()
        data = eastmoney.fetchFund(code)
        models = []
        for item in data:
            tradeDate = datetime.strptime(item["trade_date"], "%Y-%m-%d").date()
            if tradeDate > startdate:
                model = self.fundDailyBarDao.getByDate(code, tradeDate)
                if model is None:
                    model = FundDailyBar()

                model.code = code
                model.trade_date = tradeDate
                model.net_asset_value = item["net"]
                model.accumulative_net_value = item["acc"]
                if item["net"] == 1.0 and "change" not in item:
                    item["change"] = 0
                model.net_value_change = item["change"]

                models.append(model)

        self.fundDailyBarDao.addAll(models)
        print("Fund %s has %d data updated!" % (code, len(models)))
        time.sleep(1)
    
    ## Download fund net value from eastmoney and update into sql
    def updateAllFund(self):
        codes = self.dealDao.getAllFundCodes()
        for code in codes:
            startdate = self.fundDailyBarDao.getLatestTradeDate(code)
            print(code, startdate)
            self.downloadFundData(code, startdate)


if __name__ == "__main__":
    fund = FundManager()
    fund.updateAllFund()
    # fund.downloadFundData('000478', date(2018, 5, 4))

    

