import pymysql
from DBUtils.PersistentDB import PersistentDB
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

class dbsql():
    def __init__(self, pool):
        self.pool = pool
        self.connect = None
        self.cursor = None
        self.box = QMessageBox()
    def execsql(self, sql):
        result = []
        try:
            self.connect = self.pool.connection()
            self.cursor = self.connect.cursor()
            try:
                self.cursor.execute('set autocommit=0;')
                for sql1 in sql:
                    if not sql1:
                        break
                    # print(sql1)
                    self.cursor.execute(sql1)
                    result.append(self.cursor.fetchall())
                self.connect.commit()
                self.cursor.close()
                self.connect.close()
            except pymysql.Error as e:
                self.box.setText('数据操作失败！'+str(e.args[0])+' '+str(e.args[1]))
                self.box.setWindowTitle('有误')
                self.box.exec_()
                self.connect.rollback()

        except pymysql.Error as e:
            print(e.args[0], e.args[1])
            self.box.setText('数据库连接失败！'+str(e.args[0])+' '+str(e.args[1]))
            self.box.setWindowTitle('有误')
            self.box.exec_()
            self.connect.rollback()

        return result

