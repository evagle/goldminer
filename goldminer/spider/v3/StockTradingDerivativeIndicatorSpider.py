# coding: utf-8
from goldminer.models.models import TradingDerivativeIndicator
from goldminer.spider.v3.BaseFundamentalSpider import BaseFundamentalSpider


class StockTradingDerivativeIndicatorSpider(BaseFundamentalSpider):

    def __init__(self):
        super(StockTradingDerivativeIndicatorSpider, self).__init__()
        self.modelClass = TradingDerivativeIndicator
        self.table = 'trading_derivative_indicator'
        self.fields = 'DY,EV,EVEBITDA,EVPS,LYDY,NEGOTIABLEMV,PB,PCLFY,PCTTM,PELFY,PELFYNPAAEI,PEMRQ,PEMRQNPAAEI,PETTM,PETTMNPAAEI,PSLFY,PSMRQ,PSTTM,TCLOSE,TOTMKTCAP,TRADEDATE,TURNRATE,TOTAL_SHARE,FLOW_SHARE'


if __name__ == "__main__":
    spider = StockTradingDerivativeIndicatorSpider()
    spider.downloadByCode('000001')
