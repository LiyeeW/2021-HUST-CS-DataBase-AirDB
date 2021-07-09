import ui_administor
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import datetime
import dbsql
from PyQt5 import QtCore
import inputdialog
from functools import partial


class administor(ui_administor.Ui_MainWindow):
    def __init__(self, mainwindow, pool, date):
        self.setupUi(mainwindow)

        # connect airdb
        self.pool = pool
        self.dbsql = dbsql.dbsql(self.pool)

        # set statusbar
        self.date = date
        self.label = QLabel()
        self.label.setText('今日  '+str(date))
        self.statusbar.addPermanentWidget(self.label)
        self.input_dialog = None

        # each for a tab
        self.table_tab_list = []
        self.sql_tab_list = []
        self.col_tab_list = []
        self.lab_input_list = []
        self.table_tab_list.append(QTableWidget(self.tab))
        self.table_tab_list.append(QTableWidget(self.tab_2))
        self.table_tab_list.append(QTableWidget(self.tab_3))
        self.table_tab_list.append(QTableWidget(self.tab_4))
        self.table_tab_list.append(QTableWidget(self.tab_5))
        self.sql_tab_list.append(['select name, (select count(*) from city where city.pid=province.id),'
                                  '(select count(*) from airport where airport.cid in '
                                  '(select id from city where city.pid=province.id)) as anum '
                                  'from province order by anum desc;'])
        self.sql_tab_list.append(['select name, (select name from province where city.pid=province.id),'
                                  '(select count(*) from airport where airport.cid=city.id) as n'
                                  ' from city order by n desc, name desc;'])
        self.sql_tab_list.append(['select airport.name, code, city.name from '
                                  'city inner join airport on airport.cid=city.id '
                                  'order by code asc;'])
        self.sql_tab_list.append(['select name, debit1, debit2 from company order by name;'])
        self.sql_tab_list.append(['select name, numf, numc, numy from aircraft order by name;'])
        self.col_tab_list.append(['省份', '城市数量', '机场数量'])
        self.col_tab_list.append(['城市', '所属省份', '机场数量'])
        self.col_tab_list.append(['机场', '三字码', '所属城市'])
        self.col_tab_list.append(['航司', '4h退单罚款', '24h退单罚款'])
        self.col_tab_list.append(['机型', '头等舱数量', '商务舱数量', '经济舱数量'])
        self.lab_input_list.append(['省份'])
        self.lab_input_list.append(['城市', '所属省份'])
        self.lab_input_list.append(['机场', '三字码', '所属城市'])
        self.lab_input_list.append(['航司'])
        self.lab_input_list.append(['机型', '头等舱数量', '商务舱数量', '经济舱数量'])
        self.setupAllTables()

        # about sql
        self.table_name = ['province', 'city', 'airport', 'company', 'aircraft']

        self.pushButton_2.clicked.connect(self.addNew)

    def setupAllTables(self):
        for i in range(5):
            # right click to modify or delete
            self.table_tab_list[i].setContextMenuPolicy(Qt.CustomContextMenu)
            self.table_tab_list[i].customContextMenuRequested[QPoint].connect(partial(self.clickTable, i))
            # shape
            self.table_tab_list[i].setGeometry(QtCore.QRect(12, 10, 380, 220))
            # no edit
            self.table_tab_list[i].setEditTriggers(QAbstractItemView.NoEditTriggers)
            # set column
            self.table_tab_list[i].setColumnCount(len(self.col_tab_list[i]))
            self.table_tab_list[i].setHorizontalHeaderLabels(self.col_tab_list[i])
            # fill row data
            self.fillTable(i)

    def fillTable(self, index):
        # print(self.sql_tab_list[index])
        data = self.dbsql.execsql(self.sql_tab_list[index])[0]
        self.table_tab_list[index].setRowCount(len(data))
        for i in range(len(data)):
            for j in range(len(self.col_tab_list[index])):
                self.table_tab_list[index].setItem(i, j, QTableWidgetItem(str(data[i][j])))


    def clickTable(self, index, pos):
        # find out selected row
        selected_row = -1
        for i in self.table_tab_list[index].selectionModel().selection().indexes():
            selected_row = i.row()
        if selected_row == -1:
            return
        # menu match action
        menu = QMenu()
        order_1 = menu.addAction(u'修改')
        order_2 = menu.addAction(u'删除')
        action = menu.exec_(self.table_tab_list[index].mapToGlobal(pos))
        # modify
        if action == order_1:
            # get input:
            old_list = self.getOldList(index, selected_row)
            lab_list = self.lab_input_list[index]
            self.input_dialog = inputdialog.inputDialog(lab_list, old_list)
            new_list = self.input_dialog.getData()
            self.input_dialog.close()
            # update
            if new_list != old_list and new_list:
                self.sqlUpdate(old_list, new_list, index)
                # update regarding GUI
                self.updateGUI(index)
        # delete
        elif action == order_2:
            unique = [self.table_tab_list[index].item(selected_row, 0).text()]
            if index == 1:
                unique.append(self.table_tab_list[index].item(selected_row, 1).text())
            self.sqlDelete(unique, index)
            # update regarding GUI
            self.updateGUI(index)

    def sqlUpdate(self, old_list, new_list, index):
        if index == 0:
            sql_new = 'name="%s"' % (new_list[0])
            sql_old = 'name="%s"' % (old_list[0])
        elif index == 1:
            sql_new = 'name="%s", pid=(select id from province where name="%s")' % (new_list[0], new_list[1])
            sql_old = 'name="%s" and pid=(select id from province where name="%s")' % (old_list[0], old_list[1])
        elif index == 2:
            sql_new = 'name="%s", code="%s", cid=(select id from city where name="%s")' % (new_list[0], new_list[1], new_list[2])
            sql_old = 'code="%s"' % (old_list[0])
        elif index == 3:
            sql_new = 'name="%s"' % (new_list[0])
            sql_old = 'name="%s"' % (old_list[0])
        else:
            sql_new = 'name="%s", numf=%s, numc=%s, numy=%s' % (new_list[0], new_list[1], new_list[2], new_list[3])
            sql_old = 'name="%s"' % (new_list[0])

        sql1 = 'update %s set %s where %s;' % (self.table_name[index], sql_new, sql_old)
        print(sql1)
        self.dbsql.execsql([sql1])

    def sqlDelete(self, unique, index):
        if index == 0:
            sql_where = 'name="%s"' % (unique[0])
        elif index == 1:
            sql_where = 'name="%s" and pid=(select id from province where name="%s")' % (unique[0], unique[1])
        elif index == 2:
            sql_where = 'code="%s"' % (unique[0])
        elif index == 3:
            sql_where = 'name="%s"' % (unique[0])
        else:
            sql_where = 'name="%s"' % (unique[0])

        sql1 = 'delete from %s where %s;' % (self.table_name[index], sql_where)
        print(sql1)
        self.dbsql.execsql([sql1])

    def sqlInsert(self, new_list, index):
        if not new_list:
            return
        if index == 0:
            sql_new = '(0,"%s")' % (new_list[0])
        elif index == 1:
            sql_new = '(0,(select id from province where name="%s"), "%s")' % (new_list[1], new_list[0])
        elif index == 2:
            sql_new = '(0,"%s",(select id from city where name="%s"),"%s")' \
                      % (new_list[0], new_list[2], new_list[1])
        elif index == 3:
            sql_new = '(0,"%s","000000",0.7,0.3)' % (new_list[0])
        else:
            sql_new = '(0,"%s",%s,%s,%s)' % (new_list[0], new_list[1], new_list[2], new_list[3])

        sql1 = 'insert into %s value %s;' % (self.table_name[index], sql_new)
        print(sql1)
        # self.dbsql.execsql([sql1])

    def addNew(self):
        index = self.tabWidget.currentIndex()
        # get input:
        old_list = self.getOldList(index, -1)  # blank
        lab_list = self.lab_input_list[index]
        self.input_dialog = inputdialog.inputDialog(lab_list, old_list)
        new_list = self.input_dialog.getData()
        self.input_dialog.close()
        # update
        self.sqlInsert(new_list, index)
        # update regarding GUI
        self.updateGUI(index)

    def updateGUI(self, index):
        if index == 0:
            self.fillTable(0)
            self.fillTable(1)
        elif index == 1:
            self.fillTable(0)
            self.fillTable(1)
            self.fillTable(2)
        elif index == 2:
            self.fillTable(0)
            self.fillTable(1)
            self.fillTable(2)
        elif index == 3:
            self.fillTable(3)
        else:
            self.fillTable(4)

    def getOldList(self, index, row):
        old_list = []
        space = [1, 2, 3, 1, 4]
        if row == -1:
            for i in range(space[index]):
                old_list.append("")
            return old_list
        if index == 0:
            old_list.append(self.table_tab_list[index].item(row, 0).text())
        elif index == 1:
            old_list.append(self.table_tab_list[index].item(row, 0).text())
            old_list.append(self.table_tab_list[index].item(row, 1).text())
        elif index == 2:
            old_list.append(self.table_tab_list[index].item(row, 0).text())
            old_list.append(self.table_tab_list[index].item(row, 1).text())
            old_list.append(self.table_tab_list[index].item(row, 2).text())
        elif index == 3:
            old_list.append(self.table_tab_list[index].item(row, 0).text())
        elif index == 4:
            old_list.append(self.table_tab_list[index].item(row, 0).text())
            old_list.append(self.table_tab_list[index].item(row, 1).text())
            old_list.append(self.table_tab_list[index].item(row, 2).text())
            old_list.append(self.table_tab_list[index].item(row, 3).text())
        return old_list






