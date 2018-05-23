# coding: utf-8
import math


class Utils:
    @staticmethod
    def getPropertiesOfClazz(clazz):
        properties = []
        for i in dir(clazz):
            if i[0:1] != "_":
                properties.append(i)
        return properties

    '''
    Compare whether 2 constituent dict are equal
    '''
    @staticmethod
    def isConstituentsEqual(constituentA: dict, constituentB: dict):
        if constituentA.keys() != constituentB.keys():
            return False
        else:
            for k in constituentA.keys():
                if math.fabs(constituentA[k] - constituentB[k]) > 1e6:
                    return False
        return True

