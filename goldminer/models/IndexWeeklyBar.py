# coding: utf-8

class IndexWeeklyBar:
    def __init__(self):
        pass
        # code = Column(String(16), nullable=False)
        # start_date = Column(Date, nullable=False)
        # end_date = Column(Date, nullable=False)
        # open = Column(Float, nullable=False)
        # close = Column(Float, nullable=False)
        # high = Column(Float, nullable=False)
        # low = Column(Float, nullable=False)
        # amount = Column(Float(asdecimal=True), nullable=False)
        # volume = Column(BigInteger, nullable=False)
        # pre_close = Column(Float)

    def __str__(self):
        attributes = []
        for i in dir(self):
            if i[0:1] != "_":
                attributes.append(i)

        str = ""
        for attr in attributes:
            if attr in ["metadata", "to_dict", "to_str"]:
                continue
            val = getattr(self, attr)
            str = str + ("%s=%s,\t" % (attr, val))
        return str
