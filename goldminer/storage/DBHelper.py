# coding: utf-8
import pymysql
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker



class DBHelper:
    __engine = create_engine('mysql+pymysql://pocketpet:3MjdvUuXqxca6cbc@unionfight.citypet.cn:3306/goldminer?charset=utf8',
                           pool_recycle=60)
    __DBSessionClass = sessionmaker(bind=__engine, autoflush=False, autocommit=False, expire_on_commit=False)
    __session = __DBSessionClass()
    __pymysql_conn = pymysql.connect(host="unionfight.citypet.cn", port=3306, user='pocketpet', password='3MjdvUuXqxca6cbc', db='goldminer')

    @staticmethod
    def getSession() -> Session:
        return DBHelper.__session

    @staticmethod
    def getEngine():
        return DBHelper.__engine

    @staticmethod
    def getPymysqlConn():
        return DBHelper.__pymysql_conn
