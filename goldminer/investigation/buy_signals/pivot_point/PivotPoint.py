# coding: utf-8
from datetime import date

from goldminer.common.Utils import Utils
from goldminer.common.logger import get_logger

from goldminer.investigation.buy_signals.BuyPointBase import BuyPointBase
from goldminer.storage.StockCustomIndicatorDao import StockCustomIndicatorDao
from goldminer.storage.StockDailyBarAdjustNoneDao import StockDailyBarAdjustNoneDao
from goldminer.storage.StockDao import StockDao

logger = get_logger(__name__)


class PivotPoint(BuyPointBase):
    def __init__(self):
        super(BuyPointBase, self).__init__()
        self.customIndicatorDao = StockCustomIndicatorDao()
        self.stockDao = StockDao()
        self.stockBarNoAdjustDao = StockDailyBarAdjustNoneDao()


    """
    口袋支点

    MA5:MA(C,5);
    MA10:MA(C,10);
    MA20:MA(C,20);
    MA30:MA(C,30);
    MA50:MA(C,50);
    MA120:MA(C,120);
    MA250:MA(C,250);

    S_MA5:=SLOPE(MA5,2);
    S_MA10:=SLOPE(MA10,2);
    S_MA20:=SLOPE(MA20,2);
    S_MA30:=SLOPE(MA30,2);
    S_MA50:=SLOPE(MA50,2);
    S_MA120:=SLOPE(MA120,20);

    COUNT_SLP:=IF(S_MA5>0.01,1,0)+IF(S_MA10>0.01,1,0)+IF(S_MA20>0.01,1,0)+IF(S_MA30>0.01,1,0);

    MA_V50:=MA(V,50);
    V_RATIO:=V*100/MA_V50;

    GREEN_V:=IF(C<O,V,0);

    {10日内最大阴线的成交量}
    MAX_GREEN_V_10:=HHV(GREEN_V,10);

    {成交量小于50日平均成交量}
    LT_MA_V50:=IF(V<MA_V50, 1, 0);
    CNT_LT_MA_V50:=COUNT(LT_MA_V50,10);

    RED:=IF(C>O,1,0);

    {均线最大值-最小值}
    MINAVG:=MIN(MA5,MIN(MA10,MIN(MA20,MIN(MA30,MIN(MA50,MIN(MA50,MA50))))));
    MAXAVG:=MAX(MA5,MAX(MA10,MAX(MA20,MAX(MA30,MAX(MA50,MAX(MA50,MA50))))));
    CONVERGE:=(MAXAVG-MINAVG)/MINAVG*100;

    {收盘点位置至少在K线上半部分, 因为放量如果收下半部分说明上方供给很多}
    C_POSITION:=(C-L)*100/(H-L);


    {笑傲牛熊第二阶段，突破30周均线，30周均线向上,改成120日线}

    SECOND_PHASE:=S_MA120 > 0 AND C > MA120;

    NH:=IF(C>=HHV(C,10),1,0);


    {CNT_LT_MA_V50 >=3 或 >=4 需要统计一下再确认，先用宽松一点的>=3}
    SIGNAL:=V_RATIO > 125 AND RED AND V >= MAX_GREEN_V_10 AND
    CNT_LT_MA_V50 >= 3 AND CONVERGE < 10 AND
    S_MA50 > 0 AND COUNT_SLP >= 3 AND C_POSITION > 50 AND NH;


    DRAWICON(BARSSINCEN(SIGNAL,5)=0,LOW,25);


    """
    def generate_signals(self, code):
        """
        Generate pivot point signals for stock 'code'
        :return:
        """
        bars = self.stockBarNoAdjustDao.getAll(code)
        bars = Utils.pre_adjust(bars)
        if bars is None:
            logger.warn("No bars found for stock {}".format(code))
            return None

        Utils.sma(bars, [5, 10, 20, 30, 50])
        Utils.sma(bars, [50], "volume")
        last_signal_index = 0

        signals = []

        for i in range(50, len(bars)):
            bar = bars[i]
            S_MA5 = bar.sma5 / bars[i - 1].sma5 - 1
            S_MA10 = bar.sma10 / bars[i - 1].sma10 - 1
            S_MA20 = bar.sma20 / bars[i - 1].sma20 - 1
            S_MA30 = bar.sma30 / bars[i - 1].sma30 - 1
            S_MA50 = bar.sma50 / bars[i - 1].sma50 - 1

            COUNT_SLOPE_GT_Zero = int(S_MA5 > 0) + int(S_MA10 > 0) + int(S_MA20 > 0) + int(S_MA30 > 0)

            V_Ratio = bar.volume * 100 / bar.sma_volume50

            Max_Green_V10 = 0 # 10日最大成交量
            CNT_LT_MA_V50 = 0 # 小于50日平均成交量的bar数量
            NH_C10 = True # close 10日内最高
            NH_H10 = True # high 10日内最高

            for j in range(1, 10):
                prebar = bars[i-j]
                if prebar.close < prebar.open:
                    Max_Green_V10 = max(prebar.volume, Max_Green_V10)
                if prebar.volume < prebar.sma_volume50:
                    CNT_LT_MA_V50 += 1
                if prebar.close > bar.close:
                    NH_C10 = False
                if prebar.high > bar.high:
                    NH_H10 = False
            NH = NH_H10 or NH_C10

            Red_Bar = bar.close > bar.open
            minMA = min(bar.sma5, bar.sma10, bar.sma20, bar.sma30, bar.sma50)
            maxMA = max(bar.sma5, bar.sma10, bar.sma20, bar.sma30, bar.sma50)

            Converge = (maxMA - minMA) / minMA * 100

            if bar.high == bar.low:
                C_Position = 100
            else:
                C_Position = (bar.close - bar.low) * 100 / (bar.high - bar.low)

            signal = V_Ratio > 125 and Red_Bar and bar.volume >= Max_Green_V10 and CNT_LT_MA_V50 >= 3 and \
                     Converge < 10 and S_MA50 > 0 and COUNT_SLOPE_GT_Zero >= 3 and C_Position > 50 and NH

            # 5日内没有过口袋支点
            if signal and i - last_signal_index > 5:
                last_signal_index = i
                signals.append([bar.code, bar.trade_date])
        logger.info("code {} , signals = {}".format(code, signals))
        return signals

    def clear_pivot_point(self, code):
        sql =  "UPDATE StockCustomIndicator set pivot_point=NULL WHERE code='{}'".format(code)
        self.customIndicatorDao.engine.execute(sql)

    def save_pivot_point_signals(self, signals):
        if len(signals) == 0:
            return

        sql_values = ["(\"{}\",\"{}\",1)".format(code, date.strftime("%Y-%m-%d")) for code, date in signals]
        sql = 'replace into StockCustomIndicator (`code`,`trade_date`,`pivot_point`) values {};'.format(",".join(sql_values))
        self.customIndicatorDao.engine.execute(sql)
        logger.info("code {} save {} pivot points".format(signals[0][0], len(signals)))

    def clearAll(self):
        stocks = self.stockDao.getStockList()
        for code in stocks:
            self.clear_pivot_point(code)

    def processAll(self):
        stocks = self.stockDao.getStockList()
        for code in stocks:
            signals = self.generate_signals(code)
            self.save_pivot_point_signals(signals)


if __name__ == "__main__":
    processor = PivotPoint()
    signals = processor.generate_signals('601298')
    processor.save_pivot_point_signals(signals)