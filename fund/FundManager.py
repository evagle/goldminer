
# coding: utf-8

# In[26]:


# coding=utf-8
from EastMoney import EastMoney

import sys
sys.path.append('../')
from storage.DB import *


class FundManager:
    def __init__(self):
        self.db = DB()
        
    def getPersonalAssetManagement(self):
        sql = "SELECT * FROM `personal_assets_management`";
        results = self.db.executeSql(sql)
        return results
    
    def getUniqueCodeList(self):
        lst = []
        sql = "SELECT distinct(code) FROM `personal_assets_management`";
        results = self.db.executeSql(sql)
        for item in results:
            if item[0] not in lst:
                lst.append(item[0])
        return lst
    
    def getFundBarLastDate(self, code):
        sql = "SELECT trade_date FROM `fund_bar` where code = '%s' order by trade_date desc limit 1" % code
        results = self.db.executeSql(sql)
        if len(results) == 0:
            return datetime(2017,1,1).date()
        return results[0][0]
    
    def downloadFundData(self, code, startdate):
        eastmoney = EastMoney()
        data = eastmoney.fundHistory(code)
        count = 0
        for item in data:
            tradetime = datetime.strptime(item["trade_date"], "%Y-%m-%d")
            if tradetime.date() > startdate: 
                sql = "INSERT IGNORE INTO `fund_bar` (code, trade_date, net_asset_value, accumulative_net_value, net_value_change)" +                 " VALUES ('%s', '%s', %f, %f, %f)";
                sql = sql % (code, item["trade_date"], item["net"], item["acc"],item["change"])
                print(self.db.executeSql(sql))
                count += 1
        print("Fund %s has %d data updated!" % (code, count))
        time.sleep(1)
    
    ## Download fund net value from eastmoney and update into sql
    def updateAllFund(self):
        codes = self.getUniqueCodeList()
        for code in codes:
            startdate = self.getFundBarLastDate(code)
            self.downloadFundData(code, startdate)

# fund = FundManager()
# fund.updateAllFund()

    

