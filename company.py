from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtCore, QtGui, QtWidgets
from functools import partial
import pymysql
from DBUtils.PersistentDB import PersistentDB
import dbsql
import datetime
import inputdialog


class company(QMainWindow):

    close_signal = pyqtSignal()

    def __init__(self, dialog, date, cid, cname, parent=None):
        super(company, self).__init__(parent)
        # if self exits, dialog will be rejected
        self.inputDialog = None
        self.dialog = dialog
        self.box = QMessageBox()
        self.close_signal.connect(partial(self.dialog.reject))
        # set date
        self.date = date
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        # set statusbar
        self.label_15 = QLabel()
        self.label_15.setText('今日  ' + str(self.date))
        self.statusbar.addPermanentWidget(self.label_15)
        self.cid = cid
        self.cname = cname
        # connect airdb
        self.db_host = 'localhost'
        self.db_user = cname
        self.db_name = 'airdb'
        self.db_code = 'utf8'
        self.db_port = 3306
        self.pool = PersistentDB(creator=pymysql, maxusage=None,
                                 host=self.db_host, user=self.db_user,
                                  db=self.db_name,
                                 port=self.db_port, charset=self.db_code,
                                 setsession=['SET AUTOCOMMIT = 1'])
        self.dbsql = dbsql.dbsql(self.pool)
        self.setupUi()

        # set up flight_table
        self.flight_table = QTableWidget(self.tab_1)
        self.flight_col_label = ['航班号', '机型', '预计起飞', '预计到达', '准点率',
                                 '有效期开始', '有效期结束', '头等舱均价', '商务舱均价', '经济舱均价']
        self.flight_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.flight_table.customContextMenuRequested[QPoint].connect(partial(self.handleFlight))


        # set up flight_table
        self.fly_table = QTableWidget(self.tab_2)
        self.fly_col_label = ['日期', '已飞', '起飞', '到达', '头等舱价', '商务舱价', '经济舱价']
        self.fly_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.fly_table.customContextMenuRequested[QPoint].connect(partial(self.handlefly))


        # set up flight_table
        self.ticket_table = QTableWidget(self.tab)
        self.ticket_col_label = ['乘客身份证号', '舱位', '状态', '订单号', '座位', '取票码']
        #connect
        self.pushButton.clicked.connect(partial(self.close))
        self.pushButton_2.clicked.connect(self.addFlight)

        #flight_table
        self.showFlight()

    def closeEvent(self, event):
        self.close_signal.emit()
        event.accept()

    def showTicket(self):
        self.ticket_table.setGeometry(QtCore.QRect(12, 10, 380, 220))
        self.ticket_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ticket_table.setColumnCount(len(self.ticket_col_label))
        self.ticket_table.setHorizontalHeaderLabels(self.ticket_col_label)
        sql1 = 'select * from cad_ticket where ffid=%s;' % str(self.fly_id)
        data = self.dbsql.execsql([sql1])[0]
        self.ticket_table.setRowCount(len(data))
        for i in range(len(data)):
            for j in range(len(self.ticket_col_label)):
                self.ticket_table.setItem(i, j, QTableWidgetItem(str(data[i][j + 1])))

    def handlefly(self, pos):
        # find out selected row
        selected_row = -1
        for i in self.fly_table.selectionModel().selection().indexes():
            selected_row = i.row()
        if selected_row == -1:
            return
        # menu match action
        menu = QMenu()
        order_1 = menu.addAction(u'修改')
        order_2 = menu.addAction(u'机票')
        action = menu.exec_(self.fly_table.mapToGlobal(pos))
        # modify
        if action == order_1:
            self.inputDialog = inputdialog.inputDialog(['价格变动（元）'], [''])
            price_in = self.inputDialog.getData()
            if not price_in:
                return
            price_in = int(price_in[0])
            temp1 = self.fly_data[selected_row][6] + price_in
            temp2 = self.fly_data[selected_row][7] + price_in
            temp3 = self.fly_data[selected_row][8] + price_in
            sql1 = 'update cad_fly set pricef=%s,pricec=%s,pricey=%s where id=%s;' % \
                   (str(temp1), str(temp2),
                    str(temp3), str(self.fly_data[selected_row][0]))
            self.dbsql.execsql([sql1])
            self.showFly()
        elif action == order_2:
            self.fly_id = self.fly_data[selected_row][0]
            self.showTicket()
            self.tabWidget.setCurrentIndex(2)

    def showFly(self):
        self.fly_table.setGeometry(QtCore.QRect(12, 10, 380, 220))
        self.fly_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.fly_table.setColumnCount(len(self.fly_col_label))
        self.fly_table.setHorizontalHeaderLabels(self.fly_col_label)
        sql1 = 'select * from cad_fly where fid=%s;' % str(self.flight_id)
        data = self.dbsql.execsql([sql1])[0]
        self.fly_data = []
        self.fly_table.setRowCount(len(data))
        for i in range(len(data)):
            self.fly_data.append(data[i])
            for j in range(len(self.fly_col_label)):
                self.fly_table.setItem(i, j, QTableWidgetItem(str(data[i][j+2])))

    def handleFlight(self, pos):
        # find out selected row
        selected_row = -1
        for i in self.flight_table.selectionModel().selection().indexes():
            selected_row = i.row()
        if selected_row == -1:
            return
        # menu match action
        menu = QMenu()
        order_1 = menu.addAction(u'修改')
        order_2 = menu.addAction(u'实飞')
        action = menu.exec_(self.flight_table.mapToGlobal(pos))
        # modify
        if action == order_1:
            self.inputDialog = inputdialog.inputDialog(['延长有效期天数'], [''])
            days_in = self.inputDialog.getData()
            if not days_in:
                return
            days_in = int(days_in[0])
            self.inputDialog.close()
            temp1 = self.flight_data[selected_row][10] + datetime.timedelta(days=days_in)
            sql1 = 'update cad_flight set end="%s" where id=%s;' % (str(temp1), str(self.flight_data[selected_row][0]))
            self.dbsql.execsql([sql1])
            self.showFlight()
        elif action == order_2:
            self.flight_id = self.flight_data[selected_row][0]
            self.showFly()
            self.tabWidget.setCurrentIndex(1)

    def showFlight(self):
        self.flight_table.setGeometry(QtCore.QRect(12, 10, 380, 220))
        self.flight_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.flight_table.setColumnCount(len(self.flight_col_label))
        self.flight_table.setHorizontalHeaderLabels(self.flight_col_label)
        sql1 = 'select *, (select name from aircraft where aircraft.id=acid) from cad_flight;'
        data = self.dbsql.execsql([sql1])[0]
        self.flight_data =[]
        self.flight_table.setRowCount(len(data))
        id_list = [1, 14, 6, 7, 8, 9, 10, 11, 12, 13]
        for i in range(len(data)):
            self.flight_data.append(data[i])
            for j in range(len(self.flight_col_label)):
                self.flight_table.setItem(i, j, QTableWidgetItem(str(data[i][id_list[j]])))

    def addFlight(self):
        lab_list = ['航班号', '机型编号', '出发机场编号', '到达机场编号', '预计出发时间', '预计到达时间',
                    '准点率', '生效起', '生效止', '头等舱均价', '商务舱均价', '经济舱均价']
        old_list = []
        for i in range(len(lab_list)):
            old_list.append('')
        self.inputDialog = inputdialog.inputDialog(lab_list, old_list)
        new_list = self.inputDialog.getData()
        self.inputDialog.close()
        if not new_list:
            return
        new_str = '(0,'
        print(new_list)
        for i in range(len(new_list)):
            if i in (0, 4, 5, 7, 8):
                temp_str = '"%s",' % new_list[i]
            else:
                temp_str = '%s,' % new_list[i]
            new_str += temp_str
            if i==0:
                new_str += str(self.cid)+','
        sql1 = 'insert into cad_flight value '+new_str[0:-1] + ');'
        print(sql1)
        self.dbsql.execsql([sql1])
        self.showFlight()

    def setupUi(self):
        self.setObjectName("MainWindow")
        self.resize(524, 341)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(50, 40, 411, 261))
        self.tabWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tabWidget.setObjectName("tabWidget")
        self.tab_1 = QtWidgets.QWidget()
        self.tab_1.setObjectName("tab_1")
        self.tabWidget.addTab(self.tab_1, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabWidget.addTab(self.tab_2, "")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.tabWidget.addTab(self.tab, "")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(380, 20, 75, 23))
        self.pushButton.setObjectName("pushButton")
        self.label_11 = QtWidgets.QLabel(self.centralwidget)
        self.label_11.setGeometry(QtCore.QRect(50, 20, 54, 12))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_11.setFont(font)
        self.label_11.setObjectName("label_11")
        self.label_12 = QtWidgets.QLabel(self.centralwidget)
        self.label_12.setGeometry(QtCore.QRect(100, 17, 90, 17))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_12.setFont(font)
        self.label_12.setObjectName("label_12")
        self.pushButton_2 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_2.setGeometry(QtCore.QRect(300, 20, 75, 23))
        self.pushButton_2.setObjectName("pushButton_2")
        self.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self)
        self.setTabOrder(self.tabWidget, self.pushButton_2)
        self.setTabOrder(self.pushButton_2, self.pushButton)
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "航司用户：航班票务系统"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_1), _translate("MainWindow", "航班"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "实飞"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "座位"))
        self.pushButton.setText(_translate("MainWindow", "返回"))
        self.label_11.setText(_translate("MainWindow", "Hello, "))
        self.label_12.setText(_translate("MainWindow", "xxx"))
        self.pushButton_2.setText(_translate("MainWindow", "新增航班"))
        self.label_12.setText(self.cname)