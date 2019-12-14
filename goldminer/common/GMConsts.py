# coding: utf-8
from datetime import date

ADJUST_NONE = 0  # 不复权
ADJUST_PREV = 1  # 前复权
ADJUST_POST = 2  # 后复权

ABNORMAL_MAX_PE = 1000  # PE极端值，大于1000时记录成1000
ABNORMAL_MIN_PE = -1000  # PE极端值，小于-1000时记录成-1000

IQR_FACTOR = 1.5

CS_INDEX = "csindex"
CN_INDEX = "cnindex"
MYQUANT = "myquant"

MIN_GAIN = -1e6

TRADE_INIT_DATE = date(2005, 1, 1)

GET_FUNDAMENTAL_BATCH_SIZE = 40
