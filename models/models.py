# coding: utf-8
from sqlalchemy import BigInteger, Column, Date, DateTime, Float, Index, Integer, String, Text, text
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
metadata = Base.metadata


class BalanceSheet(Base):
    __tablename__ = 'BalanceSheet'
    __table_args__ = (
        Index('code_pub_date_end_date', 'code', 'pub_date', 'end_date', unique=True),
    )

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False)
    pub_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    ACCHELDFORS = Column(Float(asdecimal=True))
    ACCOPAYA = Column(Float(asdecimal=True))
    ACCORECE = Column(Float(asdecimal=True))
    ACCREXPE = Column(Float(asdecimal=True))
    ACCUDEPR = Column(Float(asdecimal=True))
    ACTITRADSECU = Column(Float(asdecimal=True))
    ACTIUNDESECU = Column(Float(asdecimal=True))
    ADVAPAYM = Column(Float(asdecimal=True))
    AVAISELLASSE = Column(Float(asdecimal=True))
    BDSPAYA = Column(Float(asdecimal=True))
    BDSPAYAPERBOND = Column(Float(asdecimal=True))
    BDSPAYAPREST = Column(Float(asdecimal=True))
    CAPISURP = Column(Float(asdecimal=True))
    CENBANKBORR = Column(Float(asdecimal=True))
    COMASSE = Column(Float(asdecimal=True))
    CONSPROG = Column(Float(asdecimal=True))
    COPEPOUN = Column(Float(asdecimal=True))
    COPEWITHREINRECE = Column(Float(asdecimal=True))
    COPEWORKERSAL = Column(Float(asdecimal=True))
    CURFDS = Column(Float(asdecimal=True))
    CURTRANDIFF = Column(Float(asdecimal=True))
    DEFEINCOTAXLIAB = Column(Float(asdecimal=True))
    DEFEREVE = Column(Float(asdecimal=True))
    DEFETAXASSET = Column(Float(asdecimal=True))
    DEPOSIT = Column(Float(asdecimal=True))
    DERIFINAASSET = Column(Float(asdecimal=True))
    DERILIAB = Column(Float(asdecimal=True))
    DEVEEXPE = Column(Float(asdecimal=True))
    DIVIDRECE = Column(Float(asdecimal=True))
    DIVIPAYA = Column(Float(asdecimal=True))
    DOMETICKSETT = Column(Float(asdecimal=True))
    DUENONCLIAB = Column(Float(asdecimal=True))
    ENGIMATE = Column(Float(asdecimal=True))
    EQUIINVE = Column(Float(asdecimal=True))
    EXPECURRLIAB = Column(Float(asdecimal=True))
    EXPENONCLIAB = Column(Float(asdecimal=True))
    EXPINONCURRASSET = Column(Float(asdecimal=True))
    EXPOTAXREBARECE = Column(Float(asdecimal=True))
    FDSBORR = Column(Float(asdecimal=True))
    FIXEDASSECLEA = Column(Float(asdecimal=True))
    FIXEDASSEIMMO = Column(Float(asdecimal=True))
    FIXEDASSEIMPA = Column(Float(asdecimal=True))
    FIXEDASSENET = Column(Float(asdecimal=True))
    FIXEDASSENETW = Column(Float(asdecimal=True))
    GENERISKRESE = Column(Float(asdecimal=True))
    GOODWILL = Column(Float(asdecimal=True))
    HOLDINVEDUE = Column(Float(asdecimal=True))
    HYDRASSET = Column(Float(asdecimal=True))
    INSUCONTRESE = Column(Float(asdecimal=True))
    INTAASSET = Column(Float(asdecimal=True))
    INTELPAY = Column(Float(asdecimal=True))
    INTELRECE = Column(Float(asdecimal=True))
    INTEPAYA = Column(Float(asdecimal=True))
    INTERECE = Column(Float(asdecimal=True))
    INTETICKSETT = Column(Float(asdecimal=True))
    INVE = Column(Float(asdecimal=True))
    INVEPROP = Column(Float(asdecimal=True))
    LCOPEWORKERSAL = Column(Float(asdecimal=True))
    LENDANDLOAN = Column(Float(asdecimal=True))
    LIABHELDFORS = Column(Float(asdecimal=True))
    LOGPREPEXPE = Column(Float(asdecimal=True))
    LONGBORR = Column(Float(asdecimal=True))
    LONGDEFEINCO = Column(Float(asdecimal=True))
    LONGPAYA = Column(Float(asdecimal=True))
    LONGRECE = Column(Float(asdecimal=True))
    MARGRECE = Column(Float(asdecimal=True))
    MARGREQU = Column(Float(asdecimal=True))
    MINYSHARRIGH = Column(Float(asdecimal=True))
    NOTESPAYA = Column(Float(asdecimal=True))
    NOTESRECE = Column(Float(asdecimal=True))
    OCL = Column(Float(asdecimal=True))
    OTHEQUIN = Column(Float(asdecimal=True))
    OTHERCURRASSE = Column(Float(asdecimal=True))
    OTHERCURRELIABI = Column(Float(asdecimal=True))
    OTHERFEEPAYA = Column(Float(asdecimal=True))
    OTHERLONGINVE = Column(Float(asdecimal=True))
    OTHERNONCASSE = Column(Float(asdecimal=True))
    OTHERNONCLIABI = Column(Float(asdecimal=True))
    OTHERPAY = Column(Float(asdecimal=True))
    OTHERRECE = Column(Float(asdecimal=True))
    PAIDINCAPI = Column(Float(asdecimal=True))
    PARESHARRIGH = Column(Float(asdecimal=True))
    PERBOND = Column(Float(asdecimal=True))
    PLAC = Column(Float(asdecimal=True))
    PREMRECE = Column(Float(asdecimal=True))
    PREP = Column(Float(asdecimal=True))
    PREPEXPE = Column(Float(asdecimal=True))
    PREST = Column(Float(asdecimal=True))
    PRODASSE = Column(Float(asdecimal=True))
    PUBLISHDATE = Column(Float(asdecimal=True))
    PURCRESAASSET = Column(Float(asdecimal=True))
    REINCONTRESE = Column(Float(asdecimal=True))
    REINRECE = Column(Float(asdecimal=True))
    RESE = Column(Float(asdecimal=True))
    RIGHAGGR = Column(Float(asdecimal=True))
    SELLREPASSE = Column(Float(asdecimal=True))
    SETTRESEDEPO = Column(Float(asdecimal=True))
    SFORMATCURRASSE = Column(Float(asdecimal=True))
    SFORMATCURRELIABI = Column(Float(asdecimal=True))
    SFORMATNONCASSE = Column(Float(asdecimal=True))
    SFORMATNONCLIAB = Column(Float(asdecimal=True))
    SFORMATPARESHARRIGH = Column(Float(asdecimal=True))
    SFORMATRIGHAGGR = Column(Float(asdecimal=True))
    SFORMATTOTASSET = Column(Float(asdecimal=True))
    SFORMATTOTLIAB = Column(Float(asdecimal=True))
    SFORMATTOTLIABSHAREQUI = Column(Float(asdecimal=True))
    SHORTTERMBDSPAYA = Column(Float(asdecimal=True))
    SHORTTERMBORR = Column(Float(asdecimal=True))
    SMERGERCURRASSE = Column(Float(asdecimal=True))
    SMERGERCURRELIABI = Column(Float(asdecimal=True))
    SMERGERNONCASSE = Column(Float(asdecimal=True))
    SMERGERNONCLIAB = Column(Float(asdecimal=True))
    SMERGERPARESHARRIGH = Column(Float(asdecimal=True))
    SMERGERRIGHAGGR = Column(Float(asdecimal=True))
    SMERGERTOTASSET = Column(Float(asdecimal=True))
    SMERGERTOTLIAB = Column(Float(asdecimal=True))
    SMERGERTOTLIABSHAREQUI = Column(Float(asdecimal=True))
    SPECPAYA = Column(Float(asdecimal=True))
    SPECRESE = Column(Float(asdecimal=True))
    SUBSRECE = Column(Float(asdecimal=True))
    SUNEVENASSETLIABEUQI = Column(Float(asdecimal=True))
    SUNEVENCURRASSE = Column(Float(asdecimal=True))
    SUNEVENCURRELIABI = Column(Float(asdecimal=True))
    SUNEVENNONCASSE = Column(Float(asdecimal=True))
    SUNEVENNONCLIAB = Column(Float(asdecimal=True))
    SUNEVENPARESHARRIGH = Column(Float(asdecimal=True))
    SUNEVENRIGHAGGR = Column(Float(asdecimal=True))
    SUNEVENTOTASSET = Column(Float(asdecimal=True))
    SUNEVENTOTLIAB = Column(Float(asdecimal=True))
    SUNEVENTOTLIABSHAREQUI = Column(Float(asdecimal=True))
    TAXESPAYA = Column(Float(asdecimal=True))
    TOPAYCASHDIVI = Column(Float(asdecimal=True))
    TOTALCURRLIAB = Column(Float(asdecimal=True))
    TOTALNONCASSETS = Column(Float(asdecimal=True))
    TOTALNONCLIAB = Column(Float(asdecimal=True))
    TOTASSET = Column(Float(asdecimal=True))
    TOTCURRASSET = Column(Float(asdecimal=True))
    TOTLIAB = Column(Float(asdecimal=True))
    TOTLIABSHAREQUI = Column(Float(asdecimal=True))
    TRADFINASSET = Column(Float(asdecimal=True))
    TRADFINLIAB = Column(Float(asdecimal=True))
    TRADSHARTRAD = Column(Float(asdecimal=True))
    TREASTK = Column(Float(asdecimal=True))
    UNDIPROF = Column(Float(asdecimal=True))
    UNREINVELOSS = Column(Float(asdecimal=True))
    UNSEG = Column(Float(asdecimal=True))
    WARLIABRESE = Column(Float(asdecimal=True))


class StockDailyBarAdjustNone(Base):
    __tablename__ = 'StockDailyBarAdjustNone'
    __table_args__ = (
        Index('code_date', 'code', 'trade_date', unique=True),
    )

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False)
    trade_date = Column(Date, nullable=False)
    open = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    amount = Column(Float(asdecimal=True), nullable=False)
    volume = Column(BigInteger, nullable=False)
    position = Column(Float)
    sec_level = Column(Integer)
    is_suspended = Column(Integer)
    pre_close = Column(Float)
    upper_limit = Column(Float)
    lower_limit = Column(Float)
    adj_factor = Column(Float(asdecimal=True), nullable=False)


class StockDailyBarAdjustPrev(Base):
    __tablename__ = 'StockDailyBarAdjustPrev'
    __table_args__ = (
        Index('code_date', 'code', 'trade_date', unique=True),
    )

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False)
    trade_date = Column(Date, nullable=False)
    open = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    amount = Column(Float(asdecimal=True), nullable=False)
    volume = Column(BigInteger, nullable=False)
    position = Column(Float)
    sec_level = Column(Integer)
    is_suspended = Column(Integer)
    pre_close = Column(Float)
    upper_limit = Column(Float)
    lower_limit = Column(Float)
    adj_factor = Column(Float(asdecimal=True))


class CashflowStatement(Base):
    __tablename__ = 'CashflowStatement'

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False)
    pub_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    ACCREXPEINCR = Column(Float(asdecimal=True))
    ACQUASSETCASH = Column(Float(asdecimal=True))
    ASSEDEPR = Column(Float(asdecimal=True))
    ASSEIMPA = Column(Float(asdecimal=True))
    BANKLOANNETINCR = Column(Float(asdecimal=True))
    BIZCASHINFL = Column(Float(asdecimal=True))
    BIZCASHOUTF = Column(Float(asdecimal=True))
    BIZNETCFLOW = Column(Float(asdecimal=True))
    CASHFINALBALA = Column(Float(asdecimal=True))
    CASHNETI = Column(Float(asdecimal=True))
    CASHNETR = Column(Float(asdecimal=True))
    CASHOPENBALA = Column(Float(asdecimal=True))
    CHARINTECASH = Column(Float(asdecimal=True))
    CHGEXCHGCHGS = Column(Float(asdecimal=True))
    DEBTINTOCAPI = Column(Float(asdecimal=True))
    DEBTPAYCASH = Column(Float(asdecimal=True))
    DEFEINCOINCR = Column(Float(asdecimal=True))
    DEFETAXASSETDECR = Column(Float(asdecimal=True))
    DEFETAXLIABINCR = Column(Float(asdecimal=True))
    DEPONETR = Column(Float(asdecimal=True))
    DISPFIXEDASSETLOSS = Column(Float(asdecimal=True))
    DISPTRADNETINCR = Column(Float(asdecimal=True))
    DIVIPROFPAYCASH = Column(Float(asdecimal=True))
    EQUFINALBALA = Column(Float(asdecimal=True))
    EQUOPENBALA = Column(Float(asdecimal=True))
    ESTIDEBTS = Column(Float(asdecimal=True))
    EXPICONVBD = Column(Float(asdecimal=True))
    FDSBORRNETR = Column(Float(asdecimal=True))
    FINALCASHBALA = Column(Float(asdecimal=True))
    FINCASHINFL = Column(Float(asdecimal=True))
    FINCASHOUTF = Column(Float(asdecimal=True))
    FINEXPE = Column(Float(asdecimal=True))
    FINFIXEDASSET = Column(Float(asdecimal=True))
    FININSTNETR = Column(Float(asdecimal=True))
    FINNETCFLOW = Column(Float(asdecimal=True))
    FINRELACASH = Column(Float(asdecimal=True))
    FIXEDASSESCRALOSS = Column(Float(asdecimal=True))
    FIXEDASSETNETC = Column(Float(asdecimal=True))
    INCRCASHPLED = Column(Float(asdecimal=True))
    INICASHBALA = Column(Float(asdecimal=True))
    INSNETC = Column(Float(asdecimal=True))
    INSPREMCASH = Column(Float(asdecimal=True))
    INTAASSEAMOR = Column(Float(asdecimal=True))
    INVCASHINFL = Column(Float(asdecimal=True))
    INVCASHOUTF = Column(Float(asdecimal=True))
    INVELOSS = Column(Float(asdecimal=True))
    INVEREDU = Column(Float(asdecimal=True))
    INVERETUGETCASH = Column(Float(asdecimal=True))
    INVNETCASHFLOW = Column(Float(asdecimal=True))
    INVPAYC = Column(Float(asdecimal=True))
    INVRECECASH = Column(Float(asdecimal=True))
    ISSBDRECECASH = Column(Float(asdecimal=True))
    LABOPAYC = Column(Float(asdecimal=True))
    LABORGETCASH = Column(Float(asdecimal=True))
    LOANNETR = Column(Float(asdecimal=True))
    LOANSNETR = Column(Float(asdecimal=True))
    LONGDEFEEXPENAMOR = Column(Float(asdecimal=True))
    MANANETR = Column(Float(asdecimal=True))
    MINYSHARRIGH = Column(Float(asdecimal=True))
    NETPROFIT = Column(Float(asdecimal=True))
    OTHER = Column(Float(asdecimal=True))
    PAYACTICASH = Column(Float(asdecimal=True))
    PAYAINCR = Column(Float(asdecimal=True))
    PAYCOMPGOLD = Column(Float(asdecimal=True))
    PAYDIVICASH = Column(Float(asdecimal=True))
    PAYINTECASH = Column(Float(asdecimal=True))
    PAYINVECASH = Column(Float(asdecimal=True))
    PAYTAX = Column(Float(asdecimal=True))
    PAYWORKCASH = Column(Float(asdecimal=True))
    PREPEXPEDECR = Column(Float(asdecimal=True))
    PUBLISHDATE = Column(Float(asdecimal=True))
    REALESTADEP = Column(Float(asdecimal=True))
    RECEFINCASH = Column(Float(asdecimal=True))
    RECEFROMLOAN = Column(Float(asdecimal=True))
    RECEINVCASH = Column(Float(asdecimal=True))
    RECEOTHERBIZCASH = Column(Float(asdecimal=True))
    RECEREDU = Column(Float(asdecimal=True))
    REDUCASHPLED = Column(Float(asdecimal=True))
    REPNETINCR = Column(Float(asdecimal=True))
    SAVINETR = Column(Float(asdecimal=True))
    SFORMATBIZCASHINFL = Column(Float(asdecimal=True))
    SFORMATBIZCASHOUTF = Column(Float(asdecimal=True))
    SFORMATBIZNETCFLOW = Column(Float(asdecimal=True))
    SFORMATCASHNETI = Column(Float(asdecimal=True))
    SFORMATCASHNETR = Column(Float(asdecimal=True))
    SFORMATFINALCASHBALA = Column(Float(asdecimal=True))
    SFORMATFINCASHINFL = Column(Float(asdecimal=True))
    SFORMATFINCASHOUTF = Column(Float(asdecimal=True))
    SFORMATINVCASHINFL = Column(Float(asdecimal=True))
    SFORMATINVCASHOUTF = Column(Float(asdecimal=True))
    SFORMATMANANETR = Column(Float(asdecimal=True))
    SMERGERBIZCASHINFL = Column(Float(asdecimal=True))
    SMERGERBIZCASHOUTF = Column(Float(asdecimal=True))
    SMERGERBIZNETCFLOW = Column(Float(asdecimal=True))
    SMERGERCASHNETI = Column(Float(asdecimal=True))
    SMERGERCASHNETR = Column(Float(asdecimal=True))
    SMERGERFINALCASHBALA = Column(Float(asdecimal=True))
    SMERGERFINCASHINFL = Column(Float(asdecimal=True))
    SMERGERFINCASHOUTF = Column(Float(asdecimal=True))
    SMERGERFINNETCFLOW = Column(Float(asdecimal=True))
    SMERGERINVCASHINFL = Column(Float(asdecimal=True))
    SMERGERINVCASHOUTF = Column(Float(asdecimal=True))
    SMERGERINVNETCASHFLOW = Column(Float(asdecimal=True))
    SMERGERMANANETR = Column(Float(asdecimal=True))
    SUBSNETC = Column(Float(asdecimal=True))
    SUBSPAYDIVID = Column(Float(asdecimal=True))
    SUBSPAYNETCASH = Column(Float(asdecimal=True))
    SUBSRECECASH = Column(Float(asdecimal=True))
    SUNEVENBIZCASHINFL = Column(Float(asdecimal=True))
    SUNEVENBIZCASHOUTF = Column(Float(asdecimal=True))
    SUNEVENBIZNETCFLOW = Column(Float(asdecimal=True))
    SUNEVENCASHNETI = Column(Float(asdecimal=True))
    SUNEVENCASHNETIMS = Column(Float(asdecimal=True))
    SUNEVENCASHNETR = Column(Float(asdecimal=True))
    SUNEVENFINALCASHBALA = Column(Float(asdecimal=True))
    SUNEVENFINCASHINFL = Column(Float(asdecimal=True))
    SUNEVENFINCASHOUTF = Column(Float(asdecimal=True))
    SUNEVENFINNETCFLOW = Column(Float(asdecimal=True))
    SUNEVENINVCASHINFL = Column(Float(asdecimal=True))
    SUNEVENINVCASHOUTF = Column(Float(asdecimal=True))
    SUNEVENINVNETCASHFLOW = Column(Float(asdecimal=True))
    SUNEVENMANANETR = Column(Float(asdecimal=True))
    SUNEVENMANANETRMS = Column(Float(asdecimal=True))
    TAXREFD = Column(Float(asdecimal=True))
    TRADEPAYMNETR = Column(Float(asdecimal=True))
    UNFIPARACHG = Column(Float(asdecimal=True))
    UNREINVELOSS = Column(Float(asdecimal=True))
    UNSEPARACHG = Column(Float(asdecimal=True))
    VALUECHGLOSS = Column(Float(asdecimal=True))
    WITHINVGETCASH = Column(Float(asdecimal=True))


class DerivativeFinanceIndicator(Base):
    __tablename__ = 'DerivativeFinanceIndicator'

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False)
    pub_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    ACCDEPRT = Column(Float(asdecimal=True))
    ACCPAYRT = Column(Float(asdecimal=True))
    ACCPAYTDAYS = Column(Float(asdecimal=True))
    ACCRECGTURNDAYS = Column(Float(asdecimal=True))
    ACCRECGTURNRT = Column(Float(asdecimal=True))
    ASSLIABRT = Column(Float(asdecimal=True))
    CAPEXTODEPANDAMOR = Column(Float(asdecimal=True))
    CAPIMORTCONMS = Column(Float(asdecimal=True))
    CAPPRORT = Column(Float(asdecimal=True))
    CASHCONVCYCLE = Column(Float(asdecimal=True))
    CASHOPINDEX = Column(Float(asdecimal=True))
    CASHRT = Column(Float(asdecimal=True))
    COMPDEPRT = Column(Float(asdecimal=True))
    CONSVATQUICKRT = Column(Float(asdecimal=True))
    CRPS = Column(Float(asdecimal=True))
    CURASSTURNDAYS = Column(Float(asdecimal=True))
    CURASSTURNRT = Column(Float(asdecimal=True))
    CURLIABTOLTMLIABRT = Column(Float(asdecimal=True))
    CURRENTRT = Column(Float(asdecimal=True))
    DPS = Column(Float(asdecimal=True))
    EBIT = Column(Float(asdecimal=True))
    EBITDA = Column(Float(asdecimal=True))
    EBITDAMARGIN = Column(Float(asdecimal=True))
    EBITDAPS = Column(Float(asdecimal=True))
    EBITDASCOVER = Column(Float(asdecimal=True))
    EBITDATOTDEBT = Column(Float(asdecimal=True))
    EBITMARGIN = Column(Float(asdecimal=True))
    EBITPS = Column(Float(asdecimal=True))
    EBITSCOVER = Column(Float(asdecimal=True))
    EBITTOTOPI = Column(Float(asdecimal=True))
    EM = Column(Float(asdecimal=True))
    EMCONMS = Column(Float(asdecimal=True))
    EPSDILUTED = Column(Float(asdecimal=True))
    EPSDILUTEDCUT = Column(Float(asdecimal=True))
    EPSDILUTEDNEWP = Column(Float(asdecimal=True))
    EPSDILUTEDOP = Column(Float(asdecimal=True))
    EQUCONMS = Column(Float(asdecimal=True))
    EQURT = Column(Float(asdecimal=True))
    EQUTOFA = Column(Float(asdecimal=True))
    EQUTOIC = Column(Float(asdecimal=True))
    EQUTOICCONMS = Column(Float(asdecimal=True))
    EQUTOTDEBT = Column(Float(asdecimal=True))
    EQUTOTLIAB = Column(Float(asdecimal=True))
    EQUTURNRT = Column(Float(asdecimal=True))
    EQUTURNRTCONMS = Column(Float(asdecimal=True))
    FAPROPORTION = Column(Float(asdecimal=True))
    FAPRORT = Column(Float(asdecimal=True))
    FATURNDAYS = Column(Float(asdecimal=True))
    FATURNRT = Column(Float(asdecimal=True))
    FCFE = Column(Float(asdecimal=True))
    FCFEPS = Column(Float(asdecimal=True))
    FCFF = Column(Float(asdecimal=True))
    FCFFPS = Column(Float(asdecimal=True))
    FINLEXPRT = Column(Float(asdecimal=True))
    INCOTAXTOTP = Column(Float(asdecimal=True))
    INTCASHREVRT = Column(Float(asdecimal=True))
    INTEXPCONCAPINT = Column(Float(asdecimal=True))
    INTEXPCUTCAPINT = Column(Float(asdecimal=True))
    INVTOCURASSRT = Column(Float(asdecimal=True))
    INVTURNDAYS = Column(Float(asdecimal=True))
    INVTURNRT = Column(Float(asdecimal=True))
    LIQDVALUERT = Column(Float(asdecimal=True))
    LOANLOSSRESTOTLOANRT = Column(Float(asdecimal=True))
    LTMASSRT = Column(Float(asdecimal=True))
    LTMDEBT = Column(Float(asdecimal=True))
    LTMDEBTTOWORKCAP = Column(Float(asdecimal=True))
    LTMLIABTOEQU = Column(Float(asdecimal=True))
    LTMLIABTOOPCAP = Column(Float(asdecimal=True))
    LTMLIABTOTA = Column(Float(asdecimal=True))
    LTMLIABTOTACONMS = Column(Float(asdecimal=True))
    MGTEXPRT = Column(Float(asdecimal=True))
    NAPS = Column(Float(asdecimal=True))
    NAPSADJ = Column(Float(asdecimal=True))
    NAPSNEWP = Column(Float(asdecimal=True))
    NCFPS = Column(Float(asdecimal=True))
    NDEBT = Column(Float(asdecimal=True))
    NDEBTTOEQU = Column(Float(asdecimal=True))
    NFART = Column(Float(asdecimal=True))
    NITOCURASS = Column(Float(asdecimal=True))
    NNONOPITOTP = Column(Float(asdecimal=True))
    NONINTCURLIABS = Column(Float(asdecimal=True))
    NONINTNONCURLIAB = Column(Float(asdecimal=True))
    NOPCAPTURNRT = Column(Float(asdecimal=True))
    NOPI = Column(Float(asdecimal=True))
    NPCONMSTOAVGTA = Column(Float(asdecimal=True))
    NPCONMSTOTP = Column(Float(asdecimal=True))
    NPCUT = Column(Float(asdecimal=True))
    NPCUTTONP = Column(Float(asdecimal=True))
    NPGRT = Column(Float(asdecimal=True))
    NPTOAVGTA = Column(Float(asdecimal=True))
    NPTONOCONMS = Column(Float(asdecimal=True))
    NPTOTP = Column(Float(asdecimal=True))
    NTANGA = Column(Float(asdecimal=True))
    NTANGASSTONDEBT = Column(Float(asdecimal=True))
    NTANGASSTOTDEBT = Column(Float(asdecimal=True))
    NTANGASSTOTLIAB = Column(Float(asdecimal=True))
    NVALCHGIT = Column(Float(asdecimal=True))
    NVALCHGITOTP = Column(Float(asdecimal=True))
    OPANCFTOOPNI = Column(Float(asdecimal=True))
    OPANITOTP = Column(Float(asdecimal=True))
    OPCAPTOTART = Column(Float(asdecimal=True))
    OPCYCLE = Column(Float(asdecimal=True))
    OPEXPRT = Column(Float(asdecimal=True))
    OPGPMARGIN = Column(Float(asdecimal=True))
    OPICFTOTICF = Column(Float(asdecimal=True))
    OPNCFPS = Column(Float(asdecimal=True))
    OPNCFSHTINVETOSHTDEBT = Column(Float(asdecimal=True))
    OPNCFTOCAPEX = Column(Float(asdecimal=True))
    OPNCFTODEPANDAMOR = Column(Float(asdecimal=True))
    OPNCFTOINTEXP = Column(Float(asdecimal=True))
    OPNCFTOLTMLIAB = Column(Float(asdecimal=True))
    OPNCFTONDABT = Column(Float(asdecimal=True))
    OPNCFTONP = Column(Float(asdecimal=True))
    OPNCFTONPCONMS = Column(Float(asdecimal=True))
    OPNCFTOOPPRO = Column(Float(asdecimal=True))
    OPNCFTOOPTI = Column(Float(asdecimal=True))
    OPNCFTOSHTDEBT = Column(Float(asdecimal=True))
    OPNCFTOSI = Column(Float(asdecimal=True))
    OPNCFTOTA = Column(Float(asdecimal=True))
    OPNCFTOTDEBT = Column(Float(asdecimal=True))
    OPNCFTOTLIAB = Column(Float(asdecimal=True))
    OPNCFTOTNCF = Column(Float(asdecimal=True))
    OPPRORT = Column(Float(asdecimal=True))
    OPPROTOTCRT = Column(Float(asdecimal=True))
    OPPTOTP = Column(Float(asdecimal=True))
    OPREVPS = Column(Float(asdecimal=True))
    OPREVTOCURASS = Column(Float(asdecimal=True))
    PROTOTCRT = Column(Float(asdecimal=True))
    QUICKRT = Column(Float(asdecimal=True))
    REPS = Column(Float(asdecimal=True))
    ROA = Column(Float(asdecimal=True))
    ROAAANNUAL = Column(Float(asdecimal=True))
    ROAANNUAL = Column(Float(asdecimal=True))
    ROEANNUAL = Column(Float(asdecimal=True))
    ROEAVG = Column(Float(asdecimal=True))
    ROEAVGCUT = Column(Float(asdecimal=True))
    ROEBYMINNPORNPCUT = Column(Float(asdecimal=True))
    ROEDILUTED = Column(Float(asdecimal=True))
    ROEDILUTEDCUT = Column(Float(asdecimal=True))
    ROIC = Column(Float(asdecimal=True))
    ROTA = Column(Float(asdecimal=True))
    SCASHREVTOOPIRT = Column(Float(asdecimal=True))
    SCOSTRT = Column(Float(asdecimal=True))
    SGPMARGIN = Column(Float(asdecimal=True))
    SHTDEBT = Column(Float(asdecimal=True))
    SHTLIABTOTLIABRT = Column(Float(asdecimal=True))
    SNPMARGINCONMS = Column(Float(asdecimal=True))
    SRPS = Column(Float(asdecimal=True))
    TAAVG = Column(Float(asdecimal=True))
    TAGRT = Column(Float(asdecimal=True))
    TANGASSTOTA = Column(Float(asdecimal=True))
    TATURNDAYS = Column(Float(asdecimal=True))
    TATURNRT = Column(Float(asdecimal=True))
    TC = Column(Float(asdecimal=True))
    TCAP = Column(Float(asdecimal=True))
    TCEXPRT = Column(Float(asdecimal=True))
    TDEBT = Column(Float(asdecimal=True))
    TDEBTTOFART = Column(Float(asdecimal=True))
    TDEBTTOIC = Column(Float(asdecimal=True))
    TDEBTTOICCONMS = Column(Float(asdecimal=True))
    TDTOEBITDA = Column(Float(asdecimal=True))
    TOPREVPS = Column(Float(asdecimal=True))
    TOTIC = Column(Float(asdecimal=True))
    TPTOEBIT = Column(Float(asdecimal=True))
    TRIEXP = Column(Float(asdecimal=True))
    TRIEXPRT = Column(Float(asdecimal=True))
    TRIEXPTOTOPI = Column(Float(asdecimal=True))
    UPPS = Column(Float(asdecimal=True))
    WORKCAP = Column(Float(asdecimal=True))


class Dividend(Base):
    __tablename__ = 'Dividend'

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False)
    pub_date = Column(DateTime, nullable=False)
    cash_div = Column(Float, nullable=False)
    allotment_ratio = Column(Float, nullable=False)
    allotment_price = Column(Float, nullable=False)
    share_div_ratio = Column(Float, nullable=False)
    share_trans_ratio = Column(Float, nullable=False)


class Exchange(Base):
    __tablename__ = 'Exchange'

    id = Column(Integer, primary_key=True)
    name = Column(String(127), nullable=False)
    symbol = Column(String(16), nullable=False)
    description = Column(Text, nullable=False)


class FundDailyBar(Base):
    __tablename__ = 'FundDailyBar'
    __table_args__ = (
        Index('code_date', 'code', 'trade_date', unique=True),
    )

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False)
    trade_date = Column(Date, nullable=False)
    net_asset_value = Column(Float(asdecimal=True), nullable=False)
    accumulative_net_value = Column(Float(asdecimal=True), nullable=False)
    net_value_change = Column(Float(asdecimal=True), nullable=False)


class IncomeStatement(Base):
    __tablename__ = 'IncomeStatement'
    __table_args__ = (
        Index('code_pub_date_end_date', 'code', 'pub_date', 'end_date', unique=True),
    )

    id = Column( Integer, primary_key=True)
    code = Column(String(16), nullable=False)
    pub_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    ASSEIMPALOSS = Column(Float(asdecimal=True))
    ASSOINVEPROF = Column(Float(asdecimal=True))
    AVAIDISTPROF = Column(Float(asdecimal=True))
    AVAIDISTSHAREPROF = Column(Float(asdecimal=True))
    BASICEPS = Column(Float(asdecimal=True))
    BIZCOST = Column(Float(asdecimal=True))
    BIZINCO = Column(Float(asdecimal=True))
    BIZTAX = Column(Float(asdecimal=True))
    BIZTOTCOST = Column(Float(asdecimal=True))
    BIZTOTINCO = Column(Float(asdecimal=True))
    CINAFORSFV = Column(Float(asdecimal=True))
    CINALIBOFRBP = Column(Float(asdecimal=True))
    COMDIVPAYBABLE = Column(Float(asdecimal=True))
    COMPCODE = Column(Float(asdecimal=True))
    COMPINCOAMT = Column(Float(asdecimal=True))
    COMPNETEXPE = Column(Float(asdecimal=True))
    CONTRESS = Column(Float(asdecimal=True))
    CPLTOHINCO = Column(Float(asdecimal=True))
    CUSTINCO = Column(Float(asdecimal=True))
    DATASOURCE = Column(Float(asdecimal=True))
    DECLAREDATE = Column(Float(asdecimal=True))
    DEVEEXPE = Column(Float(asdecimal=True))
    DILUTEDEPS = Column(Float(asdecimal=True))
    EARLYUNDIPROF = Column(Float(asdecimal=True))
    EARNPREM = Column(Float(asdecimal=True))
    EPOCFHGL = Column(Float(asdecimal=True))
    EQUMCPOTHINCO = Column(Float(asdecimal=True))
    EUQMICOLOTHINCO = Column(Float(asdecimal=True))
    EXCHGGAIN = Column(Float(asdecimal=True))
    EXTRARBIRESE = Column(Float(asdecimal=True))
    EXTSTAFFFUND = Column(Float(asdecimal=True))
    FINEXPE = Column(Float(asdecimal=True))
    FUTULOSS = Column(Float(asdecimal=True))
    HTMCCINAFORSFV = Column(Float(asdecimal=True))
    INCOTAXEXPE = Column(Float(asdecimal=True))
    INTEEXPE = Column(Float(asdecimal=True))
    INTEGRITY = Column(Float(asdecimal=True))
    INTEINCO = Column(Float(asdecimal=True))
    INVEINCO = Column(Float(asdecimal=True))
    LEGALSURP = Column(Float(asdecimal=True))
    MAINBIZCOST = Column(Float(asdecimal=True))
    MAINBIZINCO = Column(Float(asdecimal=True))
    MANAEXPE = Column(Float(asdecimal=True))
    MERGEFORMNETPROF = Column(Float(asdecimal=True))
    MINYSHARINCO = Column(Float(asdecimal=True))
    MINYSHARINCOAMT = Column(Float(asdecimal=True))
    MINYSHARRIGH = Column(Float(asdecimal=True))
    NCPOTHINCO = Column(Float(asdecimal=True))
    NETPROFIT = Column(Float(asdecimal=True))
    NONCASSETSDISI = Column(Float(asdecimal=True))
    NONCASSETSDISL = Column(Float(asdecimal=True))
    NONOEXPE = Column(Float(asdecimal=True))
    NONOREVE = Column(Float(asdecimal=True))
    OTHERBIZCOST = Column(Float(asdecimal=True))
    OTHERBIZINCO = Column(Float(asdecimal=True))
    OTHERBIZPROF = Column(Float(asdecimal=True))
    OTHERCOMPINCO = Column(Float(asdecimal=True))
    OTHERCPLTOHINCO = Column(Float(asdecimal=True))
    OTHERREASADJU = Column(Float(asdecimal=True))
    PARECOMPINCO = Column(Float(asdecimal=True))
    PARECOMPINCOAMT = Column(Float(asdecimal=True))
    PARENETP = Column(Float(asdecimal=True))
    PERPROFIT = Column(Float(asdecimal=True))
    PEXTCCAPIFD = Column(Float(asdecimal=True))
    PEXTCDEVEFD = Column(Float(asdecimal=True))
    POLIDIVIEXPE = Column(Float(asdecimal=True))
    POUNEXPE = Column(Float(asdecimal=True))
    POUNINCO = Column(Float(asdecimal=True))
    PPROFRETUINVE = Column(Float(asdecimal=True))
    PREFSTOCKDIVI = Column(Float(asdecimal=True))
    PSUPPFLOWCAPI = Column(Float(asdecimal=True))
    PUBLISHDATE = Column(Float(asdecimal=True))
    REALSALE = Column(Float(asdecimal=True))
    REALSALECOST = Column(Float(asdecimal=True))
    REINEXPE = Column(Float(asdecimal=True))
    RUNDISPROBYRREGCAP = Column(Float(asdecimal=True))
    SALESEXPE = Column(Float(asdecimal=True))
    SFORMATAVAIDISTPROF = Column(Float(asdecimal=True))
    SFORMATAVAIDISTSHAREPROF = Column(Float(asdecimal=True))
    SFORMATBIZTOTCOST = Column(Float(asdecimal=True))
    SFORMATBIZTOTINCO = Column(Float(asdecimal=True))
    SFORMATNETPROFIT = Column(Float(asdecimal=True))
    SFORMATNETPROFITSUB = Column(Float(asdecimal=True))
    SFORMATPERPROFIT = Column(Float(asdecimal=True))
    SFORMATTOTPROFIT = Column(Float(asdecimal=True))
    SFORMATUNDIPROF = Column(Float(asdecimal=True))
    SMERGERAVAIDISTPROF = Column(Float(asdecimal=True))
    SMERGERAVAIDISTSHAREPROF = Column(Float(asdecimal=True))
    SMERGERBIZTOTCOST = Column(Float(asdecimal=True))
    SMERGERBIZTOTINCO = Column(Float(asdecimal=True))
    SMERGERCOMPINCOAMTSUB = Column(Float(asdecimal=True))
    SMERGERNETPROFIT = Column(Float(asdecimal=True))
    SMERGERNETPROFITSUB = Column(Float(asdecimal=True))
    SMERGERPERPROFIT = Column(Float(asdecimal=True))
    SMERGERTOTPROFIT = Column(Float(asdecimal=True))
    SMERGERUNDIPROF = Column(Float(asdecimal=True))
    STATEXTRUNDI = Column(Float(asdecimal=True))
    SUBSIDYINCOME = Column(Float(asdecimal=True))
    SUNEVENAVAIDISTPROF = Column(Float(asdecimal=True))
    SUNEVENAVAIDISTSHAREPROF = Column(Float(asdecimal=True))
    SUNEVENBIZTOTCOST = Column(Float(asdecimal=True))
    SUNEVENBIZTOTINCO = Column(Float(asdecimal=True))
    SUNEVENCOMPINCOAMT = Column(Float(asdecimal=True))
    SUNEVENCOMPINCOAMTSUB = Column(Float(asdecimal=True))
    SUNEVENNETPROFIT = Column(Float(asdecimal=True))
    SUNEVENNETPROFITSUB = Column(Float(asdecimal=True))
    SUNEVENOTHCOMPINCOAMT = Column(Float(asdecimal=True))
    SUNEVENPERPROFIT = Column(Float(asdecimal=True))
    SUNEVENTOTPROFIT = Column(Float(asdecimal=True))
    SUNEVENUNDIPROF = Column(Float(asdecimal=True))
    SURRGOLD = Column(Float(asdecimal=True))
    TDIFFFORCUR = Column(Float(asdecimal=True))
    TOTPROFIT = Column(Float(asdecimal=True))
    TRUSTLOSS = Column(Float(asdecimal=True))
    TURNCAPSDIVI = Column(Float(asdecimal=True))
    UNDIPROF = Column(Float(asdecimal=True))
    UNREINVELOSS = Column(Float(asdecimal=True))
    VALUECHGLOSS = Column(Float(asdecimal=True))


class IndexDailyBar(Base):
    __tablename__ = 'IndexDailyBar'
    __table_args__ = (
        Index('code_date', 'code', 'trade_date', unique=True),
    )

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False)
    trade_date = Column(Date, nullable=False)
    open = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    amount = Column(Float(asdecimal=True), nullable=False)
    volume = Column(BigInteger, nullable=False)
    position = Column(Float)
    begin_time = Column(DateTime)
    end_time = Column(DateTime)
    sec_level = Column(Integer)
    is_suspended = Column(Integer)
    pre_close = Column(Float)
    upper_limit = Column(Float)
    lower_limit = Column(Float)
    adj_factor = Column(Float)


class IndexConstituent(Base):
    __tablename__ = 'IndexConstituent'
    __table_args__ = (
        Index('code', 'code', 'trade_date', unique=True),
    )

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False)
    trade_date = Column(Date, nullable=False)
    constituents = Column(Text, nullable=False)
    no_weight = Column(Integer, nullable=False, server_default=text("'0'"))


class IndexDerivativeIndicator(Base):
    __tablename__ = 'IndexDerivativeIndicator'

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False)
    pub_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    equal_weight_pe = Column(Float(asdecimal=True))
    weighted_pe = Column(Float(asdecimal=True))
    median_pe = Column(Float(asdecimal=True))
    cape = Column(Float(asdecimal=True))
    equal_weight_pb = Column(Float(asdecimal=True))
    weighted_pb = Column(Float(asdecimal=True))
    median_pb = Column(Float(asdecimal=True))


class Indexes(Base):
    __tablename__ = 'Indexes'

    code = Column(String(10), primary_key=True)
    name = Column(String(64), nullable=False)
    exchange = Column(Integer, nullable=False)
    index_type = Column(String(64), nullable=False)
    full_name = Column(String(128), nullable=False)
    pub_date = Column(DateTime, nullable=False)
    pub_organization = Column(String(64), nullable=False)
    description = Column(Text, nullable=False)


class PrimaryFinanceIndicator(Base):
    __tablename__ = 'PrimaryFinanceIndicator'
    __table_args__ = (
        Index('code_pub_date_end_date', 'code', 'pub_date', 'end_date', unique=True),
    )

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False)
    pub_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    EBIT = Column(Float(asdecimal=True))
    EBITDA = Column(Float(asdecimal=True))
    EBITDASCOVER = Column(Float(asdecimal=True))
    EBITSCOVER = Column(Float(asdecimal=True))
    EPSBASIC = Column(Float(asdecimal=True))
    EPSBASICEPSCUT = Column(Float(asdecimal=True))
    EPSDILUTED = Column(Float(asdecimal=True))
    EPSDILUTEDCUT = Column(Float(asdecimal=True))
    EPSFULLDILUTED = Column(Float(asdecimal=True))
    EPSFULLDILUTEDCUT = Column(Float(asdecimal=True))
    EPSWEIGHTED = Column(Float(asdecimal=True))
    EPSWEIGHTEDCUT = Column(Float(asdecimal=True))
    NPCUT = Column(Float(asdecimal=True))
    OPNCFPS = Column(Float(asdecimal=True))
    ROEDILUTED = Column(Float(asdecimal=True))
    ROEDILUTEDCUT = Column(Float(asdecimal=True))
    ROEWEIGHTED = Column(Float(asdecimal=True))
    ROEWEIGHTEDCUT = Column(Float(asdecimal=True))


class SalaryFund(Base):
    __tablename__ = 'SalaryFund'

    trade_date = Column(Date, primary_key=True)
    total_assets = Column(Float(asdecimal=True), nullable=False)
    security_assets = Column(Float(asdecimal=True), nullable=False)
    cash = Column(Float(asdecimal=True), nullable=False)
    share = Column(Float(asdecimal=True), nullable=False)
    net_value = Column(Float(asdecimal=True), nullable=False)


class SalaryFundOperation(Base):
    __tablename__ = 'SalaryFundOperations'

    id = Column(Integer, primary_key=True)
    trade_date = Column(Date, nullable=False)
    trade_type = Column(String(20), nullable=False)
    code = Column(String(16), nullable=False)
    name = Column(String(64), nullable=False)
    security_type = Column(Integer, nullable=False)
    money = Column(Float(asdecimal=True), nullable=False)
    share = Column(Float(asdecimal=True), nullable=False)
    share_net_value = Column(Float(asdecimal=True), nullable=False)
    commission = Column(Float(asdecimal=True), nullable=False)
    total_money = Column(Float(asdecimal=True), nullable=False)


class SecurityType(Base):
    __tablename__ = 'SecurityType'

    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    description = Column(String(255), nullable=False)


class Stock(Base):
    __tablename__ = 'Stocks'

    code = Column(String(16), primary_key=True)
    name = Column(String(64), nullable=False)
    exchange = Column(Integer, nullable=False)
    pub_date = Column(Date, nullable=False)
    industry = Column(String(64), nullable=False)
    total_stock = Column(Float(asdecimal=True), nullable=False)
    circulation_stock = Column(Float(asdecimal=True), nullable=False)


class TradingDerivativeIndicator(Base):
    __tablename__ = 'TradingDerivativeIndicator'
    __table_args__ = (
        Index('code_pub_date', 'code', 'pub_date', unique=True),
    )

    id = Column(Integer, primary_key=True)
    code = Column(String(16), nullable=False)
    pub_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    DY = Column(Float, nullable=False)
    EV = Column(Float(asdecimal=True), nullable=False)
    EVEBITDA = Column(Float, nullable=False)
    EVPS = Column(Float, nullable=False)
    LTDATE = Column(Date)
    LYDY = Column(Float, nullable=False)
    NEGOTIABLEMV = Column(Float(asdecimal=True), nullable=False)
    PB = Column(Float, nullable=False)
    PCLFY = Column(Float, nullable=False)
    PCTTM = Column(Float, nullable=False)
    PELFY = Column(Float, nullable=False)
    PELFYNPAAEI = Column(Float, nullable=False)
    PEMRQ = Column(Float, nullable=False)
    PEMRQNPAAEI = Column(Float, nullable=False)
    PETTM = Column(Float, nullable=False)
    PETTMNPAAEI = Column(Float, nullable=False)
    PSLFY = Column(Float, nullable=False)
    PSMRQ = Column(Float, nullable=False)
    PSTTM = Column(Float, nullable=False)
    TCLOSE = Column(Float, nullable=False)
    TMSTAMP = Column(Integer)
    TOTMKTCAP = Column(Float(asdecimal=True), nullable=False)
    TRADEDATE = Column(Date, nullable=False)
    TURNRATE = Column(Float, nullable=False)
    TOTAL_SHARE = Column(Float(asdecimal=True), nullable=False)
    FLOW_SHARE = Column(Float(asdecimal=True), nullable=False)
