# coding: utf-8
from common.Utils import Utils
from storage.DBHelper import DBHelper


class BaseDao:
    def __init__(self):
        self.session = DBHelper.getSession()

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

    def getSession(self):
        return self.session
