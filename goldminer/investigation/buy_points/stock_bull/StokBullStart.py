# coding: utf-8
import decimal
import math
import random
from datetime import datetime

import numpy as np
import pandas as pd
import talib

from goldminer.common.Utils import Utils
from goldminer.investigation.buy_points.BuyPointBase import BuyPointBase
from goldminer.models.models import TradingDerivativeIndicator, IncomeStatement, PrimaryFinanceIndicator
from goldminer.spider.tushare.TSStockBarSpider import TSStockBarSpider
from goldminer.storage.StockDao import StockDao


class StockBullStart(BuyPointBase):

    # 个股牛市判断
    def daily_bar_bull(self, code):
        bars = self.stockBarNoAdjustDao.getAll(code)
        bars = Utils.pre_adjust(bars)

        derivatives = self.stockFundamentals.getAll(code, TradingDerivativeIndicator)
        primary_finance_indicators = self.stockFundamentals.getAll(code, PrimaryFinanceIndicator)
        income_statements = self.stockFundamentals.getAll(code, IncomeStatement)

        bars = Utils.sma(bars, [10, 20, 50, 120, 250])
        if bars is None:
            return (-1, -1)

        '''
        S1:=SLOPE(MA(C,10),5);{10日均线的5日斜率}
        S2:=SLOPE(MA(C,20),5);
        S3:=SLOPE(MA(C,50),5);
        S4:=SLOPE(MA(C,120),10);
        S5:=SLOPE(MA(C,250),15);
        
        M1:=MA(C,10)>MA(C,20);
        M2:=MA(C,20)>MA(C,50);
        M3:=MA(C,50)>MA(C,250);
        
        {所有均线斜率大于0，10日均线大于20日均线大于120日均线}
        S1>0.1 AND S2 > 0 AND S3 > 0 AND S4 >= 0 AND S5 >= 0 AND M1 AND M2 AND M3;
        '''

        pre = None
        for i in range(250, len(bars)):
            bar = bars[i]
            S1 = bar.sma10 > bars[i - 5].sma10
            S2 = bar.sma20 > bars[i - 5].sma20
            S3 = bar.sma50 > bars[i - 5].sma50
            S4 = bar.sma120 > bars[i - 10].sma120
            S5 = bar.sma250 > bars[i - 15].sma250

            M1 = bar.sma10 > bar.sma20
            M2 = bar.sma20 > bar.sma50
            M3 = bar.sma50 > bar.sma250
            if S1 and S2 and S3 and S4 and S5 and M1 and M2 and M3:
                if pre is None or pre.trade_date != bars[i - 1].trade_date:
                    print("\n=================")
                print(code, bar.trade_date, bar.close)
                pre = bar

    def weekly_bar_bull(self, code):
        '''
        S1:=SLOPE(MA(CW,10),3);
        S2:=SLOPE(MA(CW,20),3);
        S3:=SLOPE(MA(CW,30),3);
        S4:=SLOPE(MA(CW,50),3);

        SS1:=S1>0 AND S2>0 AND S3>0 AND S4>0;

        M1:=MA(CW,10)>MA(CW,20);
        M2:=MA(CW,20)>MA(CW,30);
        M3:=MA(CW,30)>MA(CW,50);

        MS1:=M1 AND M2 AND M3;

        GMA50:=IF(CW>MA(CW,50),1,0);
        GMAC50:=COUNT(GMA50,30);

        {最近30周周K先至少有8周在50周均线以上，至少8周在50周均线以下}
        MAC50:=GMAC50 > 8 AND GMAC50 < 23;

        {CLOSE大于10周均线}

        BULL:=SS1 AND MS1 AND MAC50;
        :param code:
        :return:
        '''

        # bars = self.stockBarAdjustPrevDao.getAll(code)
        spider = TSStockBarSpider()
        bars = spider.getDailyBars(code)
        # bars = self.stockBarNoAdjustDao.getAll(code)
        # bars = Utils.pre_adjust(bars)
        # bars = Utils.pre_adjust(bars)
        if bars is None:
            return (0, 0)

        bars = Utils.dailyBar2WeeklyBar(code, bars)
        Utils.sma(bars, [10, 20, 30, 50])

        win = 0
        lose = 0
        last = 0
        for i in range(53, len(bars)):
            if i - last < 10:
                continue

            bar = bars[i]
            S1 = bar.sma10 > bars[i - 2].sma10
            S2 = bar.sma20 > bars[i - 2].sma20
            S3 = bar.sma30 > bars[i - 2].sma30
            S4 = bar.sma50 > bars[i - 2].sma50

            SS1 = S1 > 0 and S2 > 0 and S3 > 0 and S4 > 0

            M1 = bar.sma10 > bar.sma20
            M2 = bar.sma20 > bar.sma30
            M3 = bar.sma30 > bar.sma50

            MS1 = M1 and M2 and M3

            GMAC50 = 0
            for j in range(30):
                if bars[i-j].close > bars[i-j].sma50:
                    GMAC50 += 1

            MAC50 = GMAC50 > 7 and GMAC50 < 23

            isBull = SS1 and MS1 and MAC50
            if isBull:
                last = i

                max_price = 0
                for k in range(i, len(bars)):
                    if bars[k].close < bars[i].close * 0.93:
                        break

                    if bars[k].close > max_price:
                        max_price = bars[k].close
                        days_to_max_price = k - i

                gain = (max_price - bars[i].close) * 100.0 / bars[k].close
                print(bar.end_date, bar.code, bar.close, gain, days_to_max_price)
                if gain > 0:
                    win+=1
                else:
                    lose+=1
        return (win, lose)


if __name__ == "__main__":

    analyzer = StockBullStart()
    analyzer.weekly_bar_bull('600377') # 红日药业 good
    # analyzer.weekly_bar_bull('000661') # 长春高新

    stockDao = StockDao()
    stocks = stockDao.getStockList()

    random.shuffle(stocks)
    training_data = None
    num = len(stocks)
    # for i in range(num):
    #     code = stocks[i]
    #     print("processing", i, code)
    #     try:
    #         df = analyzer.weekly_bar_bull(code)
    #         if type(df) == tuple:
    #             print("Data error ", code)
    #             continue
    #     except Exception:
    #         print("Data error ", code)
    #         continue
    #
    #     if training_data is None:
    #         training_data = df
    #     else:
    #         training_data = pd.concat([training_data, df])
    #
    # output_filename = "stock_bull_start_%d_%s.tsv" % (num, datetime.now().strftime("%Y-%m-%d"))
    # training_data.to_csv(output_filename, sep="\t", index=False)

    num = 100
    total_win = 0
    total_lose = 0
    for i in range(num):
        code = stocks[i]
        print("processing", i, code)

        (win,lose) = analyzer.weekly_bar_bull(code)
        total_win += win
        total_lose += lose
        print("******", code, win, lose)

    print("total win = ", total_win, "lose=", total_lose)