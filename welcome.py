import ui_welcome
import pymysql
from DBUtils.PersistentDB import PersistentDB
import visitor
import administor
import login
from PyQt5.QtWidgets import QMainWindow, QDialog, QMessageBox
from functools import partial
import dbsql


class welcome(ui_welcome.Ui_Dialog):
    def __init__(self, dialog):
        self.setupUi(dialog)
        self.db_host = 'localhost'
        self.db_user = 'root'
        self.db_passwd = '000000'
        self.db_name = 'airdb'
        self.db_code = 'utf8'
        self.db_port = 3306
        self.pool = PersistentDB(creator=pymysql, maxusage=None,
                                 host=self.db_host, user=self.db_user,
                                 passwd=self.db_passwd, db=self.db_name,
                                 port=self.db_port, charset=self.db_code,
                                 setsession=['SET AUTOCOMMIT = 1'])
        self.dbsql = dbsql.dbsql(self.pool)
        self.qt_id = 0
        self.qt_dict = {}
        self.user_date = self.date_get()
        self.dateEdit.setDate(self.user_date)
        self.box = QMessageBox()

        self.pushButton_1.clicked.connect(partial(self.entry, '1'))
        self.pushButton_2.clicked.connect(partial(self.entry, '2'))
        self.pushButton_3.clicked.connect(partial(self.entry, '3'))

    def date_get(self):
        sql = ['select today from datelog order by today desc limit 1;']
        result = self.dbsql.execsql(sql)
        if result[0] != ():
            return result[0][0][0]
        else:
            return self.dateEdit.dateTime().toPyDateTime().date()

    # simulate real time
    def date_update(self):
        # get use's set date
        self.user_date = self.dateEdit.dateTime().toPyDateTime().date()
        today = self.user_date
        sql = ['select today from datelog order by today desc limit 1;']
        result = self.dbsql.execsql(sql)
        if result[0] != ():
            last_date = result[0][0][0]
        # update, fix fly's status, generate some tickets
        if result[0] == () or last_date.__lt__(today):
            sql = ['insert into datelog value ("{}");'.format(today)]
            sql.append('')
            self.dbsql.execsql(sql)
        elif last_date.__gt__(today):
            self.user_date = last_date
            self.dateEdit.setDate(self.user_date)
            self.box.setText('日期不可回调！')
            self.box.setWindowTitle('有误')
            self.box.exec_()
            return -1

    def checkPorder(self):
        sql1 = 'update porder set valid=0 where valid=1 and (odate<"%s" or ' \
               '(odate="%s" and (otime+interval 15*60 second)<=TIME(NOW())));' % (self.user_date, self.user_date)
        self.dbsql.execsql([sql1])

    def entry(self, name):
        if self.date_update() == -1:
            return
        self.qt_id += 1
        # visitor
        self.checkPorder()
        if name == '1':
            self.qt_dict[self.qt_id] = QMainWindow()
            visitor.visitor(self.qt_dict[self.qt_id], self.pool, self.user_date)

        # administor
        elif name == '2':
            self.qt_dict[self.qt_id] = QMainWindow()
            administor.administor(self.qt_dict[self.qt_id], self.pool, self.user_date)

        # login
        elif name == '3':
            self.qt_dict[self.qt_id] = QDialog()
            login.login(self.qt_dict[self.qt_id], self.pool, self.user_date)

        # show
        self.qt_dict[self.qt_id].show()
        
    

