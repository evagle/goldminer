# coding: utf-8
from goldminer.models.models import DerivativeFinanceIndicator
from goldminer.spider.v3.BaseFundamentalSpider import BaseFundamentalSpider

"""
衍生财务指标
https://www.myquant.cn/docs/data/data_derive_target
"""


class StockDerivativeFinanceIndicatorSpider(BaseFundamentalSpider):

    def __init__(self):
        super(StockDerivativeFinanceIndicatorSpider, self).__init__()
        self.modelClass = DerivativeFinanceIndicator
        self.table = 'deriv_finance_indicator'
        self.fields = 'ACCDEPRT,ACCPAYRT,ACCPAYTDAYS,ACCRECGTURNDAYS,ACCRECGTURNRT,ASSLIABRT,CAPEXTODEPANDAMOR,CAPIMORTCONMS,CAPPRORT,CASHCONVCYCLE,CASHOPINDEX,CASHRT,COMPDEPRT,CONSVATQUICKRT,CRPS,CURASSTURNDAYS,CURASSTURNRT,CURLIABTOLTMLIABRT,CURRENTRT,DPS,EBIT,EBITDA,EBITDAMARGIN,EBITDAPS,EBITDASCOVER,EBITDATOTDEBT,EBITMARGIN,EBITPS,EBITSCOVER,EBITTOTOPI,EM,EMCONMS,EPSDILUTED,EPSDILUTEDCUT,EPSDILUTEDNEWP,EPSDILUTEDOP,EQUCONMS,EQURT,EQUTOFA,EQUTOIC,EQUTOICCONMS,EQUTOTDEBT,EQUTOTLIAB,EQUTURNRT,EQUTURNRTCONMS,FAPROPORTION,FAPRORT,FATURNDAYS,FATURNRT,FCFE,FCFEPS,FCFF,FCFFPS,FINLEXPRT,INCOTAXTOTP,INTCASHREVRT,INTEXPCONCAPINT,INTEXPCUTCAPINT,INVTOCURASSRT,INVTURNDAYS,INVTURNRT,LIQDVALUERT,LOANLOSSRESTOTLOANRT,LTMASSRT,LTMDEBT,LTMDEBTTOWORKCAP,LTMLIABTOEQU,LTMLIABTOOPCAP,LTMLIABTOTA,LTMLIABTOTACONMS,MGTEXPRT,NAPS,NAPSADJ,NAPSNEWP,NCFPS,NDEBT,NDEBTTOEQU,NFART,NITOCURASS,NNONOPITOTP,NONINTCURLIABS,NONINTNONCURLIAB,NOPCAPTURNRT,NOPI,NPCONMSTOAVGTA,NPCONMSTOTP,NPCUT,NPCUTTONP,NPGRT,NPTOAVGTA,NPTONOCONMS,NPTOTP,NTANGA,NTANGASSTONDEBT,NTANGASSTOTDEBT,NTANGASSTOTLIAB,NVALCHGIT,NVALCHGITOTP,OPANCFTOOPNI,OPANITOTP,OPCAPTOTART,OPCYCLE,OPEXPRT,OPGPMARGIN,OPICFTOTICF,OPNCFPS,OPNCFSHTINVETOSHTDEBT,OPNCFTOCAPEX,OPNCFTODEPANDAMOR,OPNCFTOINTEXP,OPNCFTOLTMLIAB,OPNCFTONDABT,OPNCFTONP,OPNCFTONPCONMS,OPNCFTOOPPRO,OPNCFTOOPTI,OPNCFTOSHTDEBT,OPNCFTOSI,OPNCFTOTA,OPNCFTOTDEBT,OPNCFTOTLIAB,OPNCFTOTNCF,OPPRORT,OPPROTOTCRT,OPPTOTP,OPREVPS,OPREVTOCURASS,PROTOTCRT,QUICKRT,REPS,ROA,ROAAANNUAL,ROAANNUAL,ROEANNUAL,ROEAVG,ROEAVGCUT,ROEBYMINNPORNPCUT,ROEDILUTED,ROEDILUTEDCUT,ROIC,ROTA,SCASHREVTOOPIRT,SCOSTRT,SGPMARGIN,SHTDEBT,SHTLIABTOTLIABRT,SNPMARGINCONMS,SRPS,TAAVG,TAGRT,TANGASSTOTA,TATURNDAYS,TATURNRT,TC,TCAP,TCEXPRT,TDEBT,TDEBTTOFART,TDEBTTOIC,TDEBTTOICCONMS,TDTOEBITDA,TOPREVPS,TOTIC,TPTOEBIT,TRIEXP,TRIEXPRT,TRIEXPTOTOPI,UPPS,WORKCAP'


if __name__ == "__main__":
    spider = StockDerivativeFinanceIndicatorSpider()
    spider.downloadByCode('000001')
