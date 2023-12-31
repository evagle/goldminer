# coding: utf-8
import numpy as np

from goldminer.common.Utils import Utils


def MAX(bars, field, periods):
    if len(bars) == 0 or len(periods) == 0:
        return None

    values = [getattr(bar, field) for bar in bars]

    for period in periods:
        # TBD
        max = Utils.MAX(np.array(values), period)
        attr = "max{}{}".format(field, period)
        for i in range(len(bars)):
            setattr(bars[i], attr, max[i])
    return bars


def MIN(bars, field, periods):
    if len(bars) == 0 or len(periods) == 0:
        return None

    values = [getattr(bar, field) for bar in bars]

    for period in periods:
        # TBD
        min = Utils.MIN(np.array(values), period)
        attr = "min{}{}".format(field, period)
        for i in range(len(bars)):
            setattr(bars[i], attr, min[i])
    return bars


def SMA(bars, field, periods):
    if len(bars) == 0 or len(periods) == 0:
        return None

    values = [getattr(bar, field) for bar in bars]

    for period in periods:
        sma = Utils.SMA(np.array(values), period)
        attr = "sma{}{}".format(field, period)
        for i in range(len(bars)):
            setattr(bars[i], attr, sma[i])
    return bars
