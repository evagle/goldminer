# coding=utf-8
from __future__ import absolute_import, print_function, unicode_literals

from gm.api import *

set_token('a0998908534d317105b2184afbe436a4104dc51b')

import sys
sys.path.append('../')
from storage.DB import *
from IndexManager import *

indexManager = IndexManager()
for code in indexManager.getIndexList():
    print("##", code, "##")
    bars = indexManager.queryAllBars(code)
    indexManager.saveBars(bars)
    time.sleep(0.1)
    # print(bars[0])
    # break
