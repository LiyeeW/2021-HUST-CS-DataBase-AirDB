import ui_visitor
from DBUtils.PersistentDB import PersistentDB
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, \
    QLabel, QTableWidget, QAbstractItemView, QTableWidgetItem
import datetime
import dbsql
from PyQt5 import QtCore

class visitor(ui_visitor.Ui_MainWindow):
    def __init__(self, mainwindow, pool, date):
        self.setupUi(mainwindow)
        self.qt = mainwindow
        self.pool = pool
        self.date = date
        self.label = QLabel()
        self.label.setText('今日  '+str(date))
        self.statusbar.addPermanentWidget(self.label)
        self.dbsql = dbsql.dbsql(self.pool)

        self.tableProvince = QTableWidget(self.tab)
        self.sqlProvince = ['select province.id, name, (select count(*) from city where city.pid=province.id),'
                            '(select count(*) from airport where airport.cid in ('
                            'select id from city where city.pid=province.id)) as anum'
                            ' from province order by anum desc;']
        self.colProvince = ['编号', '省份', '城市数量', '机场数量']
        self.setupTable(self.tableProvince, self.sqlProvince, self.colProvince)

        self.tableCity = QTableWidget(self.tab_2)
        self.sqlCity = ['select city.id, name, (select name from province where city.pid=province.id),'
                        '(select count(*) from airport where airport.cid=city.id) as n'
                        ' from city order by n desc, name desc;']
        self.colCity = ['编号', '城市', '所属省份', '机场数量']
        self.setupTable(self.tableCity, self.sqlCity, self.colCity)

        self.tableAirport = QTableWidget(self.tab_3)
        self.sqlAirport = ['select airport.id, airport.name, code, city.name from '
                           'city inner join airport on airport.cid=city.id '
                           'order by code asc;']
        self.colAirport = ['编号', '机场', '三字码', '所属城市']
        self.setupTable(self.tableAirport, self.sqlAirport, self.colAirport)

        self.tableCompany = QTableWidget(self.tab_4)
        self.sqlCompany = ['select company.id, name, debit1, debit2 from company order by name;']
        self.colCompany = ['编号', '航司', '4h退单罚款', '24h退单罚款']
        self.setupTable(self.tableCompany, self.sqlCompany, self.colCompany)

        self.tableAircraft = QTableWidget(self.tab_5)
        self.sqlAircraft = ['select aircraft.id, name, numf, numc, numy from aircraft order by name;']
        self.colAircraft = ['编号', '机型', '头等舱数量', '商务舱数量', '经济舱数量']
        self.setupTable(self.tableAircraft, self.sqlAircraft, self.colAircraft)

    def setupTable(self, table_widget, sql_list, column_list):
        table_widget.setGeometry(QtCore.QRect(12, 10, 380, 220))
        result = self.dbsql.execsql(sql_list)[0]
        table_widget.setRowCount(len(result))
        table_widget.setColumnCount(len(column_list))
        table_widget.setHorizontalHeaderLabels(column_list)
        table_widget.setEditTriggers(QAbstractItemView.NoEditTriggers)
        for i in range(len(result)):
            for j in range(len(column_list)):
                table_widget.setItem(i, j, QTableWidgetItem(str(result[i][j])))

