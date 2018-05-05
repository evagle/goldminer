# coding=utf-8
from __future__ import print_function, absolute_import, unicode_literals
from gm.api import *

import MySQLdb
import codecs
from datetime import *
import time

set_token('a0998908534d317105b2184afbe436a4104dc51b')

import sys
sys.path.append('../')
from DB import *
from IndexManager import *

indexManager = IndexManager()
for code in indexManager.getIndexList():
    print("##", code, "##")
    bars = indexManager.queryAllBars(code)
    indexManager.saveBars(bars)
    time.sleep(0.1)
    # print(bars[0])
    # break