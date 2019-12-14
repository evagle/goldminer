# coding: utf-8

from goldminer.common import functions
from goldminer.common.BarAttribute import BarAttribute
from goldminer.common.Utils import Utils
from goldminer.investigation.buy_signals.BuyPointBase import BuyPointBase
from goldminer.spider.tushare.TSStockBarSpider import TSStockBarSpider


class StockBullStart(BuyPointBase):

    def check_daily_bar_bull_signal(self, bars):
        """
        {
        周K牛市起点公式
          * 10，20，30，50周线斜率大于0
          * 均线10>20>30>50多头排列
          * 30周内不少于10周CLOSE小于MA50，不少于4周大于MA50
        }

        {只关注10,20,30,50周均线}

        MA5:MA(CLOSE,5);
        MA10:MA(CLOSE,10);
        MA20:MA(CLOSE,20);
        MA30:MA(CLOSE,30);
        MA50:MA(CLOSE,50);
        MA120:MA(CLOSE,120);
        MA250:MA(CLOSE,250);

        DRAWTEXT_FIX(1,0.01,0,0,'所属概念:'),COLORA8A8A8;
        DRAWTEXT_FIX(1,0.1,0,0,GNBLOCK),COLORWHITE;

        S1:=SLOPE(MA(C,10),3);
        S2:=SLOPE(MA(C,20),3);
        S3:=SLOPE(MA(C,30),3);
        S4:=SLOPE(MA(C,50),3);
        S5:=SLOPE(MA(C,120),2);
        S6:=SLOPE(MA(C,250),2);

        SS1:=S1>0 AND S2>0 AND S3>0 AND S4>0 AND (S5>0 OR S6>0);

        M1:=MA(C,10)>MA(C,20);
        M2:=MA(C,20)>MA(C,30);
        M3:=MA(C,20)>MA(C,50);
        M4:=C>MA(C,250);

        MS1:=M1 AND M2 AND M3 AND M4;

        GMA50:=IF(C>MA(C,50),1,0);
        GMAC50:=COUNT(GMA50,30);

        {最近30日K先至少有6天在50日均线以上，至少4天在50日均线以下}
        MAC50:=GMAC50 > 5 AND GMAC50 < 26;

        {CLOSE大于10周均线}

        {均线最大值-最小值}
        MINAVG:=MIN(MA5,MIN(MA10,MIN(MA20,MIN(MA30,MIN(MA50,MIN(MA120,MA120))))));
        MAXAVG:=MAX(MA5,MAX(MA10,MAX(MA20,MAX(MA30,MAX(MA50,MAX(MA120,MA120))))));
        CONVERGE:=(MAXAVG-MINAVG)/C*100;


        {CLOSE不高于年线的170%}
        CLOSE250:=C*100/MA250<170;

        NH:=IF(H<HHV(H,50),0,1);

        {1O天内曾创50日新高}
        NH50:=COUNT(NH,30);

        NN:=IF(C>MA(C,250),1,0);

        {最近30天至少3天大于年线，至少一天小于年线}
        COUNT_GT250:=COUNT(NN,30);

        {最高价距离120日内的最高价不到10%}
        NEAR_HIGH120:=HIGH/HHV(HIGH,120)>0.9;

        {新高筛选条件}
        HIGH_FILTER:=NH50 AND COUNT_GT250>2 AND NEAR_HIGH120;

        BULL:=SS1 AND MS1 AND MAC50 AND CONVERGE < 20
        AND CLOSE250 AND HIGH_FILTER ;

        DRAWICON(BARSSINCEN(BULL,10)=0,LOW,24);


        """

        if bars is None:
            return False

        i = len(bars) - 1
        bar = bars[i]
        S1 = bar.sma10 > bars[i - 2].sma10
        S2 = bar.sma20 > bars[i - 2].sma20
        S3 = bar.sma30 > bars[i - 2].sma30
        S4 = bar.sma50 > bars[i - 2].sma50
        S5 = bar.sma120 > bars[i - 1].sma120
        S6 = bar.sma250 > bars[i - 1].sma250

        SS1 = S1 > 0 and S2 > 0 and S3 > 0 and S4 > 0 and (S5 or S6)

        M1 = bar.sma10 > bar.sma20
        M2 = bar.sma20 > bar.sma30
        M3 = bar.sma20 > bar.sma50
        M4 = bar.close > bar.sma250

        MS1 = M1 and M2 and M3 and M4

        GMAC50 = 0
        for j in range(30):
            if bars[i - j].close > bars[i - j].sma50:
                GMAC50 += 1

        MAC50 = GMAC50 > 5 and GMAC50 < 26

        minimum = min(bar.sma5, bar.sma10, bar.sma20, bar.sma30, bar.sma50, bar.sma120)
        maximum = max(bar.sma5, bar.sma10, bar.sma20, bar.sma30, bar.sma50, bar.sma120)
        converge = (maximum - minimum) / bar.close * 100.0

        close250 = bar.close / bar.sma250 < 1.7

        # 3O天内曾创50日新高
        NH50_IN30 = False
        for bar in bars[-30:]:
            if bar.high >= bar.maxhigh50:
                NH50_IN30 += 1

        COUNT_GT250_IN30 = 0
        for bar in bars[-30:]:
            if bar.close > bar.sma250:
                COUNT_GT250_IN30 += 1

        # {最高价不小于120日内的最高价的90%}
        # NEAR_HIGH120: = HIGH / HHV(HIGH, 120) > 0.9;
        NEAR_HIGH120 = bar.high > bar.maxhigh120 * 0.9

        High_Filter = NH50_IN30 > 0 and COUNT_GT250_IN30 > 2 and NEAR_HIGH120

        isBull = SS1 and MS1 and MAC50 and converge < 15 and close250 and High_Filter

        return isBull

    def generate_daily_bar_bull_signals(self, code):

        bars = self.stockBarNoAdjustDao.getByCode(code)
        bars = Utils.pre_adjust(bars)
        bars = Utils.sma(bars, [5, 10, 20, 30, 50, 120, 250])
        bars = functions.MAX(bars, BarAttribute.HIGH.value, [50, 120])

        if bars is None:
            return False
        last = 0
        for i in range(120, len(bars)):
            if i - last <= 10:
                continue
            isBull = self.check_daily_bar_bull_signal(bars[:i + 1])

            if isBull:
                print(bars[i].trade_date, isBull)
                last = i

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

        # bars = self.stockBarNoAdjustDao.getAll(code)
        spider = TSStockBarSpider()
        bars = spider.getDailyBars(code)

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
    analyzer.generate_daily_bar_bull_signals('000739')
