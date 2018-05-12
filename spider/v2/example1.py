#!/usr/bin/python
# -*- coding:utf-8 -*-
##
# @file a.py
# @Brief 
# @author  Brian 
# @version 1.0
# @date 2018-03-29

from gmsdk import md
from gmsdk.api import StrategyBase


class MyStrategy(StrategyBase):
    def __init__(self, *args, **kwargs):
        super(MyStrategy, self).__init__(*args, **kwargs)
    def on_tick(self, tick):
        self.open_long(tick.exchange, tick.sec_id, tick.last_price, 100)
        print("OpenLong: exchange %s, sec_id %s, price %s" % (tick.exchange, tick.sec_id, tick.last_price))

ret = md.init("17611258516", "web4217121")
ticks = md.get_dailybars("SHSE.600000,SZSE.000001", "2015-10-29", "2015-12-29")
for tick in ticks:
    print(tick.open)
print(ticks[0].open)
if __name__ == '__main____':
    ret = MyStrategy(
        username='17611258516',
        password='web4217121',
        strategy_id='9c8a4a49-3359-11e8-8fda-001c42a1c0e2',
        subscribe_symbols='SHSE.600000.tick',
        mode=2
        ).run()
    print(('exit code: ', ret))
