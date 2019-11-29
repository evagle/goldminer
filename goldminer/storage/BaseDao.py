# coding: utf-8
from goldminer.common.Utils import Utils
from goldminer.storage.DBHelper import DBHelper


class BaseDao:
    def __init__(self):
        self.session = DBHelper.getSession()
        self.engine = DBHelper.getEngine()
        self.__cache = {}

    def add(self, instance):
        self.session.add(instance)
        self.session.commit()

    def addAll(self, instances):
        if len(instances) == 0:
            return
        modelClazz = instances[0].__class__

        properties = Utils.getPropertiesOfClazz(modelClazz)
        items = []
        for instance in instances:
            item = {}
            for p in properties:
                item[p] = getattr(instance, p)
            items.append(item)

        self.session.execute(
            modelClazz.__table__.insert(),
            items
        )
        self.session.commit()

    def merge(self, instances):
        for instance in instances:
            self.session.merge(instance)

    def getSession(self):
        return self.session

    def getCacheKey(self, code, tradeDate):
        return code + tradeDate.strftime("%Y-%m-%d")

    def getFromCache(self, code, tradeDate, clazzName):
        key = self.getCacheKey(code, tradeDate)
        if clazzName in self.__cache and key in self.__cache[clazzName]:
            return self.__cache[clazzName][key]
        return None

    def addToCache(self, code, clazzName, models):
        for model in models:
            key = self.getCacheKey(code, model.trade_date)
            if clazzName not in self.__cache:
                self.__cache[clazzName] = {}
            self.__cache[clazzName][key] = model

    def deleteCache(self, clazzName):
        self.__cache[clazzName] = {}

    def bulkSave(self, models):
        self.session.bulk_save_objects(models)
        self.session.commit()
