#coding=utf8
import MySQLdb
import ConfigParser
import os
# 获取config配置文件

def getConfig(section, key):
    #db = '/db_sf_lwq.conf'
    db = '/db_jx_test.conf'
    config = ConfigParser.ConfigParser()
    path = os.path.split(os.path.realpath(__file__))[0] + db
    config.read(path)
    return config.get(section, key)

dbhost = getConfig("database", "dbhost")
dbname = getConfig("database", "dbname")
dbuser = getConfig("database", "dbuser")
dbpassword = getConfig("database", "dbpassword")

from sqlalchemy import create_engine
engine = create_engine("mysql+mysqldb://%s:%s@%s:3306/%s?charset=utf8" % (dbuser, dbpassword, dbhost, dbname),echo=True)

DB_CONFIG = {
    'host': dbhost,
    'user': dbuser,
    'passwd': dbpassword,
    'db': dbname,
    'port': 3306,
    'charset': 'utf8'
}

ConMysql = MySQLdb.connect(**DB_CONFIG)
c = ConMysql.cursor()


def wd_save(dbTable,df):
    try:
        df.to_sql(dbTable,
                  con=engine, flavor=None,
                  if_exists='append',
                  index=False, )
    except Exception as e:                           # 抓出数据库的错误异常
        e_type = str(type(e))[18:]
        print e_type + str(e)