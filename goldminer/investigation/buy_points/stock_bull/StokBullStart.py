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
        '''
        {
        日K线牛市起点公式
          * 10，20，30，50日线斜率大于0
          * 均线10>(20,30)>50多头排列
          * 最近30周周K先至少有6天在50日均线以上，至少6天在50日均线以下
        }


        MA5:=MA(CLOSE,5);
        MA10:=MA(CLOSE,10);
        MA20:=MA(CLOSE,20);
        MA30:=MA(CLOSE,30);
        MA50:=MA(CLOSE,50);
        MA120:=MA(CLOSE,120);
        MA250:=MA(CLOSE,250);

        S1:=SLOPE(MA(C,10),3);
        S2:=SLOPE(MA(C,20),3);
        S3:=SLOPE(MA(C,30),3);
        S4:=SLOPE(MA(C,50),3);

        SS1:=S1>0 AND S2>0 AND S3>0 AND S4>0;

        M1:=MA(C,10)>MA(C,20);
        M2:=MA(C,20)>MA(C,30);
        {M3:=MA(C,30)>MA(C,50);}
        {30 > 50 VS 20>50}
        M3:=MA(C,20)>MA(C,50);

        MS1:=M1 AND M2 AND M3;

        GMA50:=IF(C>MA50,1,0);
        GMAC50:=COUNT(GMA50,30);

        {最近30周周K先至少有6天在50日均线以上，至少6天在50日均线以下}
        MAC50:=GMAC50 > 5 AND GMAC50 < 25;

        {CLOSE大于10周均线}

        {均线最大值-最小值}
        MINAVG:=MIN(MA5,MIN(MA10,MIN(MA20,MIN(MA30,MIN(MA50,MIN(MA120,MA120))))));
        MAXAVG:=MAX(MA5,MAX(MA10,MAX(MA20,MAX(MA30,MAX(MA50,MAX(MA120,MA120))))));
        CONVERGE:=(MAXAVG-MINAVG)/C*100;

        {CLOSE不高于年线的170%}
        CLOSE250:=C*100/MA250<170;

        NH:=IF(H<HHV(H,50),0,1);

        {一月内曾创50日新高}
        NH50:=COUNT(NH,30);

        NN:=IF(C>MA(C,250),1,0);

        {最近30天至少3天大于年线，至少一天小于年线}
        COUNT_GT250:=COUNT(NN,30);

        {最高价距离120日内的最高价不到10%}
        NEAR_HIGH120:=HIGH/HHV(HIGH,120)>0.9;

        {新高筛选条件}
        HIGH_FILTER:=NH50 AND COUNT_GT250>2 AND COUNT_GT250<30 AND NEAR_HIGH120;

        BULL:=SS1 AND MS1 AND MAC50 AND CONVERGE < 15;

        {10日内没有出现过BULL信号}
        FIRST:=(BARSSINCEN(BULL,10)=0);

        {RPS250>90}
        EX2:=EXTDATA_USER(2,0);{250天的}
        RPS250:=EX2/10;
        RPS250GT0:=RPS250>95;

        {RPS120>90}
        EX1:=EXTDATA_USER(1,0);{120天的}
        RPS120:=EX1/10;
        RPS120GT0:= RPS120>95;

        RPSFILTER:=RPS250GT0 OR RPS120GT0;

        BULL AND FIRST AND RPSFILTER;

        :param code:
        :return:
        '''
        # bars = self.stockBarNoAdjustDao.getAll(code)
        # bars = Utils.pre_adjust(bars)

        spider = TSStockBarSpider()
        bars = spider.getDailyBars(code)

        bars = Utils.sma(bars, [5, 10, 20, 30, 50, 120, 250])
        if bars is None:
            return (-1, -1)

        win = 0
        lose = 0
        last = 0
        totalgain = 1
        for i in range(120, len(bars)):
            if i - last <= 30:
                continue
            bar = bars[i]
            S1 = bar.sma10 > bars[i - 2].sma10
            S2 = bar.sma20 > bars[i - 2].sma20
            S3 = bar.sma30 > bars[i - 2].sma30
            S4 = bar.sma50 > bars[i - 2].sma50

            SS1 = S1 > 0 and S2 > 0 and S3 > 0 and S4 > 0

            M1 = bar.sma10 > bar.sma20
            M2 = bar.sma20 > bar.sma30
            M3 = bar.sma20 > bar.sma50

            MS1 = M1 and M2 and M3

            GMAC50 = 0
            for j in range(30):
                if bars[i - j].close > bars[i - j].sma50:
                    GMAC50 += 1

            MAC50 = GMAC50 > 5 and GMAC50 < 25

            minimum = min(bar.sma5, bar.sma10, bar.sma20, bar.sma30, bar.sma50, bar.sma120)
            maximum = max(bar.sma5, bar.sma10, bar.sma20, bar.sma30, bar.sma50, bar.sma120)
            converge = (maximum - minimum) / bar.close * 100.0

            close250 = bar.close/bar.sma250 < 1.7


            isBull = SS1 and MS1 and MAC50 and converge < 15 and close250
            if isBull:
                last = i

                # 1. 找到第一个close小于10日线的bar j
                # 2. 从j+1开始找sma5斜率大于0的点作为买点
                # 3. 买入后，第一次跌破sma5卖出
                ############################################################
                firstBarBelowSMA10 = 0
                for j in range(i+1, len(bars)):
                    if bars[j].close < bars[j].sma10:
                        firstBarBelowSMA10 = j
                        break

                buyPoint = 0
                if firstBarBelowSMA10 > 0:
                    for j in range(firstBarBelowSMA10+1, len(bars)):
                        if bars[j].sma5 > bars[j-1].sma5:
                            buyPoint = j
                            break

                buyPrice = bars[buyPoint].close

                sellPoint = 0
                currentGain = 0
                if buyPoint > 0:
                    for j in range(buyPoint+1, len(bars)):
                        if bars[j].close < bar.close * 0.95:
                            sellPoint = j
                            break

                        if bars[j].close > bar.close * 1.15:
                            if bars[j].close < bars[j].sma20:
                                sellPoint = j
                                break
                        # elif bars[j].close > bar.close * 1.05:
                        #     if bars[j].close < bars[j].sma10:
                        #         sellPoint = j
                        #         break

                        # 利润损失30%以上卖出
                        newGain = (bars[j].close - buyPrice) / buyPrice * 100.0
                        if currentGain > 15 and newGain < currentGain * 0.66:
                            sellPoint = j
                            break
                        currentGain = newGain


                gain = 0
                if buyPoint > 0 and sellPoint > 0:
                    buyPrice = bars[buyPoint].close
                    sellPrice = bars[sellPoint].close
                    gain = (sellPrice - buyPrice) / buyPrice * 100.0
                    totalgain = totalgain * (1 + gain / 100)
                    print("signal:", bar.code, bar.trade_date,
                          "buy", bars[buyPoint].trade_date, buyPrice, "sell", bars[sellPoint].trade_date,
                          sellPrice, "gain", gain)
                else:
                    print("signal:", bar.code, bar.trade_date, "------dropped----")


                ############################################################

                # 1. 如果信号当天收正，第二天收正且大于sma5，第二天sma5,sma10,斜率为正，按照第二天close买入
                # 2. 买入后，第一次跌破sma10卖出
                ############################################################

                # buyPoint = 0
                # sellPoint = 0
                # if i < len(bars) - 1 and \
                #         bars[i + 1].close > bars[i + 1].open and \
                #         bars[i + 1].close > bars[i + 1].sma5 and \
                #         bars[i + 1].sma5 > bars[i].sma5 and \
                #         bars[i + 1].sma10 > bars[i].sma10:
                #     buyPoint = i + 1
                #
                # if buyPoint > 0 and buyPoint < len(bars) - 1:
                #     for k in range(buyPoint + 1, len(bars)):
                #         if bars[k].close < bar.close * 0.95:
                #             sellPoint = k
                #             break
                #         if bars[k].close < bars[k].sma10 and bars[k].close > bar.close * 1.05:
                #             sellPoint = k
                #             break
                #
                # gain = 0
                # if buyPoint > 0 and sellPoint > 0:
                #     buyPrice = bars[buyPoint].close
                #     sellPrice = bars[sellPoint].close
                #     gain = (sellPrice - buyPrice) / buyPrice * 100.0
                #     totalgain = totalgain * (1 + gain / 100)
                #     print("signal:", bar.code, bar.trade_date,
                #           "buy", bars[buyPoint].trade_date, buyPrice, "sell",bars[sellPoint].trade_date,
                #           sellPrice, "gain", gain, totalgain)
                # else:
                #     print("signal:", bar.code, bar.trade_date, "------dropped----")
                ############################################################

                if gain > 0:
                    win += 1
                elif gain < 0:
                    lose += 1
        print(code, "*** win", win, "lose", lose, "total gain", totalgain)
        return (win, lose)

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
                if bars[i - j].close > bars[i - j].sma50:
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
                    win += 1
                else:
                    lose += 1
        return (win, lose)


if __name__ == "__main__":

    analyzer = StockBullStart()
    analyzer.daily_bar_bull('600984')
    # analyzer.daily_bar_bull('002234')
    exit(0)
    stockDao = StockDao()
    stocks = stockDao.getStockList()

    random.shuffle(stocks)
    training_data = None
    num = len(stocks)
    num = 100
    total_win = 0
    total_lose = 0
    for i in range(num):
        code = stocks[i]
        print("processing", i, code)

        (win, lose) = analyzer.daily_bar_bull(code)
        total_win += win
        total_lose += lose
        print("******", code, win, lose)

    print("total win = ", total_win, "lose=", total_lose)
