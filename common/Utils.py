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

    @staticmethod
    def isDictEqual(dictA: dict, dictB: dict):
        if dictA.keys() != dictB.keys():
            return False
        else:
            for k in dictA.keys():
                if math.fabs(dictA[k] - dictB[k]) > 1e6:
                    return False
        return True

    @staticmethod
    def isListEqual(listA: list, listB: list):
        if len(listA) != len(listB):
            return False
        else:
            for k in listA:
                if k not in listB:
                    return False
        return True
