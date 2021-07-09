import sys
from functools import partial
import ui_login
from DBUtils.PersistentDB import PersistentDB
from PyQt5.QtCore import Qt,pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QLabel, QMessageBox
import datetime
import dbsql
import user
import company


class login(ui_login.Ui_Dialog):
    def __init__(self, dialog, pool, date):
        self.setupUi(dialog)
        self.qt = dialog
        self.window = None

        self.date = date

        # connect airdb
        self.pool = pool
        self.dbsql = dbsql.dbsql(self.pool)

        self.name = ''
        self.passwd = ''
        self.choice = self.radioButton.isChecked()
        self.id = 0
        self.pushButton.clicked.connect(partial(self.searchUser))
        self.pushButton_2.clicked.connect(partial(self.createUser))
        self.box = QMessageBox()


    def logIn(self):
        self.qt.hide()
        if self.choice:
            self.window = user.user(self.qt, self.pool, self.date, self.id)
            self.window.show()

            # self.window.close_signal.connect(partial(self.qt.reject))
        else:
            self.window = company.company(self.qt, self.date, self.id, self.name)
            self.window.show()

    def searchUser(self):
        self.name = self.lineEdit.text()
        self.passwd = self.lineEdit_2.text()
        self.choice = self.radioButton.isChecked()
        if self.choice:
            table_name = 'user'
        else:
            table_name = 'company'
        sql1 = 'select id, passwd from %s where name="%s";' % (table_name, self.name)
        result = self.dbsql.execsql([sql1])[0]
        # print(result)
        # result = result[0]
        if result == ():
            self.box.setText('该用户不存在！')
            self.box.setWindowTitle('有误')
            self.box.exec_()
        elif result[0][1] != self.passwd:
            self.box.setText('密码不正确！')
            self.box.setWindowTitle('有误')
            self.box.exec_()
        else:
            self.id = result[0][0]
            self.logIn()


    def createUser(self):
        self.name = self.lineEdit.text()
        self.passwd = self.lineEdit_2.text()
        self.choice = self.radioButton.isChecked()
        if self.choice:
            table_name = 'user'
        else:
            table_name = 'company'
        sql1 = 'select id from %s where name="%s";' % (table_name, self.name)
        result = self.dbsql.execsql([sql1])[0]
        if result != ():
            self.box.setText('该用户已存在！')
            self.box.setWindowTitle('有误')
            self.box.exec_()
            return
        if self.choice:
            sql1 = 'null,0'
        else:
            sql1 = '0.7,0.3'
        sql1 = 'insert into %s value (0,"%s","%s",%s);' % (table_name, self.name, self.passwd, sql1)
        print(sql1)
        if not self.choice:
            sql = []
            sql.append('create user %s;' % self.name)
            sql.append('grant company_ad to %s;' % self.name)
            sql.append('update mysql.user set Grant_priv="Y", Super_priv="Y" where user = "%s";' % self.name)
            sql.append('set default role all to %s;' % self.name)
            sql.append('flush privileges;')
            self.dbsql.execsql(sql)
        self.dbsql.execsql([sql1])
        self.box.setText('注册成功！')
        self.box.setWindowTitle('完成')
        self.box.exec_()

