import configparser
import os
import sys
import json
import pymysql

class DbManager:

    __instance = None
    _host = None
    _user = None
    _passwd = None
    _db = None

    @staticmethod
    def getInstance(DB_INFO):
        """ Static access method. """
        print(f"getInstance start")
        if DbManager.__instance == None:
            DbManager.__instance = DbManager()
            DbManager._host = DB_INFO['host']
            DbManager._user = DB_INFO['user']
            DbManager._passwd = DB_INFO['passwd']
            DbManager._db = DB_INFO['db']
        return DbManager.__instance

    def __init__(self):
        pass

    def select_sql(self,sql_string):
        result = None
        try:
            conn = pymysql.connect(host=self._host, user=self._user, password=self._passwd,
                                   db=self._db,
                                   charset='utf8')
            curs = conn.cursor()
            curs.execute(sql_string)
            result = curs.fetchall()
        except Exception as e:
            print(e)
        finally:
            conn.close()
        return result

    def run_sql(self, sql_string, raw_data=None):
        try:
            conn = pymysql.connect(host=self._host, user=self._user, password=self._passwd,
                                   db=self._db,
                                   charset='utf8')
            curs = conn.cursor()
            if raw_data:
                curs.execute(query=sql_string, args=(raw_data))
            else:
                curs.execute(sql_string)
                conn.commit()
            
        except Exception as e:
            print(e)
        finally:
            conn.close()

if __name__ == '__main__':
    # example 1
    # print(ConfManager.getInstance().getSysConfigData("MSGQUEUE_INFO", "PLTEIB"))
    # print(ConfManager.getInstance().getSysConfigData("MSGQUEUE_INFO", "proc2"))
    DB_INFO = {'host': '192.168.1.132', 'port': 3306, 'passwd': 'Dlxndl@123', 'user': 'e2e', 'db': 'e2edb'}
    sql_string = 'select * from e2edb.test_tbl'
#    sql_string = 'INSERT INTO e2edb.test_tbl VALUES (2)'
    # dbmanger = DbManager(DB_INFO)
#    result = DbManager().getInstance(DB_INFO).run_sql(sql_string)
    result = DbManager().getInstance(DB_INFO).select_sql(sql_string)
    print(result)

    string ="   "
    str_len = len(string)
    print(f"str_len ={str_len}")

