# coding=utf-8
from __future__ import print_function, absolute_import, unicode_literals
from gm.api import *

import MySQLdb
import codecs
from datetime import *
import time
import sys
sys.path.append('../')
from DB import *
from StockManager import *
from IndexManager import *
from FundamentalsManager import *

set_token('a0998908534d317105b2184afbe436a4104dc51b')

fieldstr = 'ASSEIMPALOSS,ASSOINVEPROF,AVAIDISTPROF,AVAIDISTSHAREPROF,BASICEPS,BIZCOST,BIZINCO,BIZTAX,BIZTOTCOST,BIZTOTINCO,CINAFORSFV,CINALIBOFRBP,COMDIVPAYBABLE,COMPCODE,COMPINCOAMT,COMPNETEXPE,CONTRESS,CPLTOHINCO,CUSTINCO,DEVEEXPE,DILUTEDEPS,EARLYUNDIPROF,EARNPREM,EPOCFHGL,EQUMCPOTHINCO,EUQMICOLOTHINCO,EXCHGGAIN,EXTRARBIRESE,EXTSTAFFFUND,FINEXPE,FUTULOSS,HTMCCINAFORSFV,INCOTAXEXPE,INTEEXPE,INTEINCO,INVEINCO,LEGALSURP,MAINBIZCOST,MAINBIZINCO,MANAEXPE,MERGEFORMNETPROF,MINYSHARINCO,MINYSHARINCOAMT,MINYSHARRIGH,NCPOTHINCO,NETPROFIT,NONCASSETSDISI,NONCASSETSDISL,NONOEXPE,NONOREVE,OTHERBIZCOST,OTHERBIZINCO,OTHERBIZPROF,OTHERCOMPINCO,OTHERCPLTOHINCO,OTHERREASADJU,PARECOMPINCO,PARECOMPINCOAMT,PARENETP,PERPROFIT,PEXTCCAPIFD,PEXTCDEVEFD,POLIDIVIEXPE,POUNEXPE,POUNINCO,PPROFRETUINVE,PREFSTOCKDIVI,PSUPPFLOWCAPI,PUBLISHDATE,REALSALE,REALSALECOST,REINEXPE,RUNDISPROBYRREGCAP,SALESEXPE,SFORMATAVAIDISTPROF,SFORMATAVAIDISTSHAREPROF,SFORMATBIZTOTCOST,SFORMATBIZTOTINCO,SFORMATNETPROFIT,SFORMATNETPROFITSUB,SFORMATPERPROFIT,SFORMATTOTPROFIT,SFORMATUNDIPROF,SMERGERAVAIDISTPROF,SMERGERAVAIDISTSHAREPROF,SMERGERBIZTOTCOST,SMERGERBIZTOTINCO,SMERGERCOMPINCOAMTSUB,SMERGERNETPROFIT,SMERGERNETPROFITSUB,SMERGERPERPROFIT,SMERGERTOTPROFIT,SMERGERUNDIPROF,STATEXTRUNDI,SUBSIDYINCOME,SUNEVENAVAIDISTPROF,SUNEVENAVAIDISTSHAREPROF,SUNEVENBIZTOTCOST,SUNEVENBIZTOTINCO,SUNEVENCOMPINCOAMT,SUNEVENCOMPINCOAMTSUB,SUNEVENNETPROFIT,SUNEVENNETPROFITSUB,SUNEVENOTHCOMPINCOAMT,SUNEVENPERPROFIT,SUNEVENTOTPROFIT,SUNEVENUNDIPROF,SURRGOLD,TDIFFFORCUR,TOTPROFIT,TRUSTLOSS,TURNCAPSDIVI,UNDIPROF,UNREINVELOSS,VALUECHGLOSS'
table = 'income_statement'
providor = FundamentalsManager()
stockManager = StockManager()

for code in stockManager.getStockList():
    print("##", code, "##")
    fundamentals = providor.getFundamentals(code, table, fieldstr)
    providor.saveFundamentals(code, fundamentals, table, fieldstr)
    time.sleep(0.1)