# coding=utf-8
from __future__ import absolute_import, print_function, unicode_literals

import sys

from gm.api import *

sys.path.append('../')
from storage.DB import *
from StockManager import *
from IndexManager import *

set_token('a0998908534d317105b2184afbe436a4104dc51b')

indexManager = IndexManager()
for code in indexManager.getIndexList():
    print("##", code, "##")
    results = indexManager.queryInstituents(code)
    indexManager.saveConstituents(code, results)
    time.sleep(1)
# data = get_history_constituents(index='SHSE.000001',start_date='2017-12-31', end_date='2017-12-31')
# print(data)