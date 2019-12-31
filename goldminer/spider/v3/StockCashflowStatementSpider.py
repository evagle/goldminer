# coding: utf-8
from goldminer.models.models import CashflowStatement
from goldminer.spider.v3.BaseFundamentalSpider import BaseFundamentalSpider


class StockCashflowStatementSpider(BaseFundamentalSpider):

    def __init__(self):
        super(StockCashflowStatementSpider, self).__init__()
        self.modelClass = CashflowStatement
        self.table = 'cashflow_statement'
        self.fields = 'ACCREXPEINCR,ACQUASSETCASH,ASSEDEPR,ASSEIMPA,BANKLOANNETINCR,BIZCASHINFL,BIZCASHOUTF,BIZNETCFLOW,CASHFINALBALA,CASHNETI,CASHNETR,CASHOPENBALA,CHARINTECASH,CHGEXCHGCHGS,DEBTINTOCAPI,DEBTPAYCASH,DEFEINCOINCR,DEFETAXASSETDECR,DEFETAXLIABINCR,DEPONETR,DISPFIXEDASSETLOSS,DISPTRADNETINCR,DIVIPROFPAYCASH,EQUFINALBALA,EQUOPENBALA,ESTIDEBTS,EXPICONVBD,FDSBORRNETR,FINALCASHBALA,FINCASHINFL,FINCASHOUTF,FINEXPE,FINFIXEDASSET,FININSTNETR,FINNETCFLOW,FINRELACASH,FIXEDASSESCRALOSS,FIXEDASSETNETC,INCRCASHPLED,INICASHBALA,INSNETC,INSPREMCASH,INTAASSEAMOR,INVCASHINFL,INVCASHOUTF,INVELOSS,INVEREDU,INVERETUGETCASH,INVNETCASHFLOW,INVPAYC,INVRECECASH,ISSBDRECECASH,LABOPAYC,LABORGETCASH,LOANNETR,LOANSNETR,LONGDEFEEXPENAMOR,MANANETR,MINYSHARRIGH,NETPROFIT,OTHER,PAYACTICASH,PAYAINCR,PAYCOMPGOLD,PAYDIVICASH,PAYINTECASH,PAYINVECASH,PAYTAX,PAYWORKCASH,PREPEXPEDECR,PUBLISHDATE,REALESTADEP,RECEFINCASH,RECEFROMLOAN,RECEINVCASH,RECEOTHERBIZCASH,RECEREDU,REDUCASHPLED,REPNETINCR,SAVINETR,SFORMATBIZCASHINFL,SFORMATBIZCASHOUTF,SFORMATBIZNETCFLOW,SFORMATCASHNETI,SFORMATCASHNETR,SFORMATFINALCASHBALA,SFORMATFINCASHINFL,SFORMATFINCASHOUTF,SFORMATINVCASHINFL,SFORMATINVCASHOUTF,SFORMATMANANETR,SMERGERBIZCASHINFL,SMERGERBIZCASHOUTF,SMERGERBIZNETCFLOW,SMERGERCASHNETI,SMERGERCASHNETR,SMERGERFINALCASHBALA,SMERGERFINCASHINFL,SMERGERFINCASHOUTF,SMERGERFINNETCFLOW,SMERGERINVCASHINFL,SMERGERINVCASHOUTF,SMERGERINVNETCASHFLOW,SMERGERMANANETR,SUBSNETC,SUBSPAYDIVID,SUBSPAYNETCASH,SUBSRECECASH,SUNEVENBIZCASHINFL,SUNEVENBIZCASHOUTF,SUNEVENBIZNETCFLOW,SUNEVENCASHNETI,SUNEVENCASHNETIMS,SUNEVENCASHNETR,SUNEVENFINALCASHBALA,SUNEVENFINCASHINFL,SUNEVENFINCASHOUTF,SUNEVENFINNETCFLOW,SUNEVENINVCASHINFL,SUNEVENINVCASHOUTF,SUNEVENINVNETCASHFLOW,SUNEVENMANANETR,SUNEVENMANANETRMS,TAXREFD,TRADEPAYMNETR,UNFIPARACHG,UNREINVELOSS,UNSEPARACHG,VALUECHGLOSS,WITHINVGETCASH'


if __name__ == "__main__":
    spider = StockCashflowStatementSpider()
    spider.downloadByCodes('000001')