# coding: utf-8
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker


class DBHelper:
    __engine = create_engine('mysql+pymysql://goldminer:goldiamond@192.168.10.212:3306/goldminer?charset=utf8',
                             pool_recycle=60)
    # expire_on_commit should be False, otherwise all data are expired and need rerun query after a commit command
    __DBSessionClass = sessionmaker(bind=__engine, autoflush=False, autocommit=False, expire_on_commit=False)
    __session = __DBSessionClass()

    @staticmethod
    def getSession() -> Session:
        return DBHelper.__session

    @staticmethod
    def getEngine():
        return DBHelper.__engine
