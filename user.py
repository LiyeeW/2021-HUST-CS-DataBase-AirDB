import ui_administor
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import QtCore, QtGui, QtWidgets
import datetime
import dbsql
from PyQt5 import QtCore
import inputdialog
from functools import partial
import selectdialog
import random
import sys
import time


class user(QMainWindow):

    close_signal = pyqtSignal()

    def __init__(self, dialog, pool, date, uid, parent=None):
        super(user, self).__init__(parent)
        # if self exits, dialog will be rejected
        self.timer = QTimer()
        self.timer.timeout.connect(self.orderTimer)
        self.dialog = dialog
        self.box = QMessageBox()
        self.close_signal.connect(partial(self.dialog.reject))
        # set date
        self.date = date
        # connect airdb
        self.pool = pool
        self.dbsql = dbsql.dbsql(self.pool)
        # set name
        self.uid = uid
        sql1 = 'select name, bkid, money, passwd from user where id = %s;' % str(self.uid)
        result = self.dbsql.execsql([sql1])[0][0]
        self.uname = result[0]
        self.bkid = result[1]
        self.money = result[2]
        self.passwd = result[3]
        self.province_list = []
        self.city_list = []
        self.airport_list = []
        self.fly_id = []
        self.fly_data = []

        # table in 1 and 3
        self.setupUi()
        self.fly_table = QTableWidget(self.tab_5)
        self.fly_col_label = ['航班号', '起飞日期', '起飞机场', '到达机场', '预计起飞时间', '预计到达时间',
                              '航空公司', '机型', '准点率', '舱位', '价格']
        self.passenger_table = QTableWidget(self.tab_3)
        self.passenger_col_label = ['身份证号', '姓名', '出生年份', '性别']
        self.order_table = QTableWidget(self.tab_2)
        self.order_col_label = ['订单号', '状态', '下单时间', '航班号', '起飞日期', '舱位', '总金额']
        # set up fly_table
        self.fly_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.fly_table.customContextMenuRequested[QPoint].connect(partial(self.createOrder))
        self.fly_table.setGeometry(QtCore.QRect(12, 10, 380, 220))
        self.fly_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.fly_table.setColumnCount(len(self.fly_col_label))
        self.fly_table.setHorizontalHeaderLabels(self.fly_col_label)
        # set up passenger_table
        self.passenger_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.passenger_table.setGeometry(QtCore.QRect(12, 10, 380, 220))
        self.passenger_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.passenger_table.setColumnCount(len(self.passenger_col_label))
        self.passenger_table.setHorizontalHeaderLabels(self.passenger_col_label)
        self.passenger_list = []
        self.showPassenger()
        # set up order_table
        self.order_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.order_table.customContextMenuRequested[QPoint].connect(partial(self.handleOrder))
        self.order_table.setGeometry(QtCore.QRect(12, 10, 380, 220))
        self.order_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.order_table.setColumnCount(len(self.order_col_label))
        self.order_table.setHorizontalHeaderLabels(self.order_col_label)

        # set up ticket_table
        self.ticket_table = QTableWidget(self.tab_6)
        self.ticket_col_label = ['编号', '乘客姓名', '取票密码', '座位号']
        self.ticket_table.setGeometry(QtCore.QRect(12, 10, 380, 220))
        self.ticket_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ticket_table.setColumnCount(len(self.ticket_col_label))
        self.ticket_table.setHorizontalHeaderLabels(self.ticket_col_label)

        self.input_dialog = None
        self.select_dialog = None

        # connect
        self.comboBox.currentIndexChanged.connect(partial(self.showCity, True))
        self.comboBox_4.currentIndexChanged.connect(partial(self.showCity, False))
        self.comboBox_2.currentIndexChanged.connect(partial(self.showAirport, True))
        self.comboBox_5.currentIndexChanged.connect(partial(self.showAirport, False))
        self.pushButton_4.clicked.connect(partial(self.queryRoute))
        self.pushButton_6.clicked.connect(partial(self.createPassenger))
        self.pushButton_7.clicked.connect(partial(self.modifyPasswd))
        self.tabWidget.currentChanged.connect(partial(self.showWhich))
        self.pushButton.clicked.connect(partial(self.close))
        self.pushButton_2.clicked.connect(partial(self.addMoney))
        self.pushButton_3.clicked.connect(partial(self.checkIn))
        self.pushButton_5.clicked.connect(partial(self.searchFlight))

    def closeEvent(self, event):
        self.close_signal.emit()
        event.accept()

    def searchFlight(self):
        fname = self.lineEdit_6.text()
        sql1 = 'select (select name from province where exists ' \
               '(select * from city where city.pid=province.id and exists ' \
               '(select * from airport where airport.cid=city.id and airport.id=flight.aid_f))), ' \
               '(select name from city where exists ' \
               '(select * from airport where airport.cid=city.id and airport.id=flight.aid_f)), ' \
               '(select name from airport where airport.id=flight.aid_f), ' \
               '(select name from province where exists ' \
               '(select * from city where city.pid=province.id and exists ' \
               '(select * from airport where airport.cid=city.id and airport.id=flight.aid_t))), ' \
               '(select name from city where exists ' \
               '(select * from airport where airport.cid=city.id and airport.id=flight.aid_t)),' \
               '(select name from airport where airport.id=flight.aid_t), ' \
               '(select name from company where company.id=flight.cid) ' \
               'from flight where flight.name="%s" ;' % fname
        print(sql1)
        result = self.dbsql.execsql([sql1])[0]
        if not result[0]:
            self.box.setText('该航班号不存在！')
            self.box.setWindowTitle('有误')
            self.box.exec_()
            return
        (off_pname, off_cname, off_aname, land_pname, land_cname, land_aname, cname) = result[0]
        off_index = self.province_list.index(off_pname)
        land_index = self.province_list.index(land_pname)
        self.comboBox.setCurrentIndex(off_index)
        self.comboBox_4.setCurrentIndex(land_index)
        self.box.setText('出发：%s-%s-%s\n抵达：%s-%s-%s\n隶属：%s' %
                         (off_pname, off_cname, off_aname, land_pname, land_cname, land_aname, cname))
        self.box.setWindowTitle('完成')
        self.box.exec_()

    def checkIn(self):
        aname = self.lineEdit_3.text()
        cname = self.lineEdit_2.text()
        pid = self.lineEdit_4.text()
        passwd = self.lineEdit_5.text()
        sql1 = 'select id from ticket where pid="%s" and passwd="%s" and exists ' \
               '(select * from porder where porder.id=oid and exists ' \
               '(select * from fly where fly.id=porder.ffid and fly.fid in ' \
               '(select id from flight where cid=(select id from company where name="%s") and ' \
               'aid_f=(select id from airport where name="%s")))) and exists ' \
               '(select * from porder where porder.id=oid and valid=2);' % (pid, passwd, cname, aname)
        print(sql1)
        tid = self.dbsql.execsql([sql1])[0]
        if not tid:
            self.box.setText('信息有误，值机失败！')
            self.box.setWindowTitle('有误')
            self.box.exec_()
            return
        tid = tid[0][0]
        sql1 = 'update ticket set seat=(select seat_ticket(%s)) where id=%s;' % (str(tid), str(tid))
        sql2 = 'select seat from ticket where id=%s;' % str(tid)
        seat_str = self.dbsql.execsql([sql1, sql2])[1]
        self.box.setText('值机成功，您的座位号为%s！' % seat_str)
        self.box.setWindowTitle('完成')
        self.box.exec_()
        return


    def orderTimer(self):
        if self.tabWidget.currentIndex() != 3:
            return
        valid_str = ['超时', '已支付', '已退订']
        for i in range(self.order_table.rowCount()):
            status = self.order_table.item(i, 1).text()
            if status not in valid_str:
                new_status = datetime.datetime.strptime(status, '%H:%M:%S') - datetime.timedelta(seconds=1)
                new_status = str(new_status.time())
                # pay out of date
                if new_status == '00:00:00':
                    oid = int(self.order_table.item(i, 0).text())
                    sql1 = 'update porder set valid=0 where id=%s;' % str(oid)
                    self.dbsql.execsql([sql1])
                    self.order_table.item(i, 1).setText('超时')
                    continue
                # update count down
                self.order_table.item(i, 1).setText(str(new_status))
        self.timer.start(1000)

    def addMoney(self):
        if self.bkid is None:
            self.box.setText('请先绑定银行卡！')
            self.box.setWindowTitle('有误')
            self.box.exec_()
            label_list = ['卡号']
            old_list = ['']
            self.input_dialog = inputdialog.inputDialog(label_list, old_list)
            new_list = self.input_dialog.getData()
            if not new_list:
                self.box.setText('充值失败！')
                self.box.setWindowTitle('有误')
                self.box.exec_()
                return
            sql1 = 'update user set bkid="%s" where id=%s;' % (new_list[0], str(self.uid))
            self.dbsql.execsql([sql1])
            self.bkid = new_list[0]
        add_money = self.lineEdit.text()
        if not str.isdigit(add_money) or int(add_money) <= 0:
            self.box.setText('输入格式有误！')
            self.box.setWindowTitle('有误')
            self.box.exec_()
        self.money += int(add_money)
        sql1 = 'update user set money=%s where id=%s;' % (str(self.money), str(self.uid))
        self.dbsql.execsql([sql1])
        self.box.setText('充值成功！')
        self.box.setWindowTitle('完成')
        self.box.exec_()
        self.showMoney()

    def modifyPasswd(self):
        label_list = ['原密码', '新密码']
        old_list = ['', '']
        self.input_dialog = inputdialog.inputDialog(label_list, old_list)
        new_list = self.input_dialog.getData()
        if not new_list:
            self.box.setText('修改失败！')
            self.box.setWindowTitle('有误')
            self.box.exec_()
            return
        if new_list[0] != self.passwd:
            self.box.setText('原密码不符！')
            self.box.setWindowTitle('有误')
            self.box.exec_()
            return
        self.passwd = new_list[1]
        sql1 = 'update user set passwd="%s" where id=%s;' % (self.passwd, str(self.uid))
        self.dbsql.execsql([sql1])
        self.box.setText('密码修改成功！')
        self.box.setWindowTitle('完成')
        self.box.exec_()

    def showWhich(self):
        index = self.tabWidget.currentIndex()
        if index == 3:
            self.timer.start(1000)
            self.showOrder()
        elif index == 4:
            self.showPassenger()
        elif index == 5:
            self.showMoney()

    def showMoney(self):
        if self.bkid is None:
            self.label_3.setText('无')
        else:
            self.label_3.setText('%s' % self.bkid)
        self.label_4.setText('%s' % str(self.money))

    def generateToken(self):
        token = ''
        for i in range(6):
            num = random.randint(0, 9)
            letter = chr(random.randint(97, 122))  # 取小写字母
            Letter = chr(random.randint(65, 90))  # 取大写字母
            s = str(random.choice([num, letter, Letter]))
            token += s
        print(token)
        return token

    def handleOrder(self, pos):
        # find out selected row
        selected_row = -1
        for i in self.order_table.selectionModel().selection().indexes():
            selected_row = i.row()
        if selected_row == -1:
            return
        # menu match action
        menu = QMenu()
        order_1 = menu.addAction(u'支付')
        order_2 = menu.addAction(u'退订')
        order_3 = menu.addAction(u'详情')
        action = menu.exec_(self.fly_table.mapToGlobal(pos))
        # pay
        if action == order_1:
            valid_str = ['超时', '已支付', '已退订']
            status = self.order_table.item(selected_row, 1).text()
            # not pay-waiting
            if status in valid_str:
                self.box.setText('%s，无法支付！' % status)
                self.box.setWindowTitle('有误')
                self.box.exec_()
                return
            price_total = self.order_table.item(selected_row, 6).text()
            # money not enough
            if self.money < int(price_total):
                self.box.setText('余额不足，请先充值！')
                self.box.setWindowTitle('有误')
                self.box.exec_()
                return
            self.money -= int(price_total)
            oid = self.order_table.item(selected_row, 0).text()
            sql1 = 'update user set money=%s where id=%s;' % (str(self.money), str(self.uid))
            sql2 = 'update porder set valid=2 where id=%s;' % oid
            sql3 = 'update ticket set passwd="%s" where oid=%s;' % (self.generateToken(), oid)
            self.dbsql.execsql([sql1, sql2, sql3])
            self.order_table.item(selected_row, 1).setText('已支付')
        # cancel order
        elif action == order_2:
            status = self.order_table.item(selected_row, 1).text()
            # not cancelable
            if status in ['超时', '已退订']:
                self.box.setText('%s，无法退订！' % status)
                self.box.setWindowTitle('有误')
                self.box.exec_()
                return
            # check flew and off_due
            oid = self.order_table.item(selected_row, 0).text()
            sql1 = 'select flew, fdate, off_due from flight inner join fly on fly.fid=flight.id where fly.id=%s;' % oid
            (flew, fdate, off_due) = self.dbsql.execsql([sql1])[0][0]
            off_due = datetime.datetime.strptime(str(off_due), '%H:%M:%S').time()
            off_datetime = datetime.datetime.combine(fdate, off_due)
            now_datetime = datetime.datetime.combine(self.date, datetime.datetime.today().time())
            if flew or now_datetime.__ge__(off_datetime):
                self.box.setText('已起飞，无法退订！')
                self.box.setWindowTitle('有误')
                self.box.exec_()
                return
            # check whether fetched
            sql1 = 'select * from ticket where oid=%s and seat is not null;' % oid
            result = self.dbsql.execsql([sql1])[0]
            if result:
                self.box.setText('存在已值机机票，无法退订！')
                self.box.setWindowTitle('有误')
                self.box.exec_()
                return
            # cancel directly
            if status != '已支付':
                sql1 = 'update porder set valid=3 where id=%s;' % oid
                self.dbsql.execsql([sql1])
                self.order_table.item(selected_row, 1).setText('已退订')
                return
            # compute debit, return money and cancel
            total_money = self.order_table.item(selected_row, 6).text()
            debit_time = off_datetime - now_datetime
            debit_time = debit_time.total_seconds()
            if debit_time > 60*60*24:
                # full return
                rate = "1"
            elif debit_time >60*60*4:
                rate = "1-(select debit2 from company where id=(select cid from flight where name='%s'))" % self.order_table.item(selected_row, 3).text()
                # return total*(1-debit2)
            else:
                rate = "1-(select debit1 from company where id=(select cid from flight where name='%s'))" % self.order_table.item(selected_row, 3).text()
                # return total*(1-debit1)
            sql1 = 'update user set money=(%s+(%s)*%s) where id=%s' % (self.money, rate, total_money, str(self.uid))
            sql2 = 'update porder set valid=3 where id=%s;' % oid
            sql3 = 'select money from user where id=%s' % str(self.uid)
            self.money = self.dbsql.execsql([sql1, sql2, sql3])[2][0][0]
            self.order_table.item(selected_row, 1).setText('已退订')
        # show ticket
        elif action == order_3:
            self.oid = int(self.order_table.item(selected_row, 0).text())
            self.tabWidget.setCurrentIndex(2)
            self.showTicket()

    def showOrder(self):
        sql1 = 'select porder.id, valid, odate, otime, flight.name, fly.fdate, stype, pricef, pricec, pricey, num' \
               ' from porder, flight, fly where porder.ffid=fly.id and fly.fid=flight.id and uid=%s ' \
               'order by porder.id desc;' % str(self.uid)
        print(sql1)
        order_list = self.dbsql.execsql([sql1])[0]
        if not order_list:
            self.order_table.setRowCount(0)
            return
        self.order_table.setRowCount(len(order_list))
        valid_str = ['超时', '待支付', '已支付', '已退订']
        type_str = ['头等舱', '商务舱', '经济舱']
        for i in range(len(order_list)):
            # id
            self.order_table.setItem(i, 0, QTableWidgetItem(str(order_list[i][0])))
            # status-valid
            valid = order_list[i][1]
            val_str = valid_str[valid]
            odate = order_list[i][2]
            otime = datetime.datetime.strptime(str(order_list[i][3]), '%H:%M:%S').time()
            if val_str == '待支付' and odate == self.date:
                passby = datetime.datetime.combine(odate, datetime.datetime.now().time()) - datetime.datetime.combine(odate, otime)
                passby = datetime.datetime.strptime(str(passby)[0:-7], '%H:%M:%S').time()
                remains = datetime.datetime.combine(odate, datetime.datetime.strptime('0:15:00', '%H:%M:%S').time()) - datetime.datetime.combine(odate, passby)
                remains = datetime.datetime.strptime(str(remains), '%H:%M:%S').time()
                # remains = remains.time()
                val_str = str(remains)
            self.order_table.setItem(i, 1, QTableWidgetItem(val_str))
            # order time
            self.order_table.setItem(i, 2, QTableWidgetItem(str(datetime.datetime.combine(odate, otime))))
            # flight name
            self.order_table.setItem(i, 3, QTableWidgetItem(str(order_list[i][4])))
            # fdate
            self.order_table.setItem(i, 4, QTableWidgetItem(str(order_list[i][5])))
            # stype
            stype = order_list[i][6]
            self.order_table.setItem(i, 5, QTableWidgetItem(type_str[stype-1]))
            # price
            price = [order_list[i][7], order_list[i][8], order_list[i][9]]
            price_total = price[stype-1] * order_list[i][10]
            self.order_table.setItem(i, 6, QTableWidgetItem(str(price_total)))

    def showTicket(self):
        sql1 = 'select id, (select name from person where id=ticket.pid), passwd, seat ' \
               'from ticket where oid=%s;' % str(self.oid)
        ticket = self.dbsql.execsql([sql1])[0]
        self.ticket_table.setRowCount(len(ticket))
        for i in range(len(ticket)):
            for j in range(2):
                self.ticket_table.setItem(i, j, QTableWidgetItem(str(ticket[i][j])))
                if not ticket[i][2]:
                    passwd_str = '未支付'
                else:
                    passwd_str = ticket[i][2]
                self.ticket_table.setItem(i, 2, QTableWidgetItem(passwd_str))
            if not ticket[i][3]:
                seat_str = '未值机'
            else:
                seat_str = ticket[i][3]
            self.ticket_table.setItem(i, 3, QTableWidgetItem(seat_str))

    def showPassenger(self):
        sql1 = 'select * from person where id in (select pid from agent where uid=%s);' % str(self.uid)
        passenger = self.dbsql.execsql([sql1])[0]
        self.passenger_table.setRowCount(len(passenger))
        self.passenger_list = []
        for i in range(len(passenger)):
            self.passenger_list.append(passenger[i][1])
            for j in range(3):
                self.passenger_table.setItem(i, j, QTableWidgetItem(str(passenger[i][j])))
            if passenger[i][3] == 0:
                sex = '女'
            else:
                sex = '男'
            self.passenger_table.setItem(i, 3, QTableWidgetItem(sex))

    def createPassenger(self):
        label_list = ['身份证号', '姓名', '出生年', '性别']
        old_list = ['', '', '', '']
        self.input_dialog = inputdialog.inputDialog(label_list, old_list)
        new_list = self.input_dialog.getData()
        self.input_dialog.close()
        if new_list == [] or len(new_list[0]) != 18 or not str.isdigit(new_list[0][0:-1]):
            self.box.setText('身份证信息有误！')
            self.box.setWindowTitle('有误')
            self.box.exec_()
            return
        if new_list[3] == '女':
            new_list[3] = 0
        elif new_list[3] == '男':
            new_list[3] = 1
        else:
            self.box.setText('性别请填‘男’或‘女’！')
            self.box.setWindowTitle('有误')
            self.box.exec_()
            return
        sql1 = 'select * from person where id="%s";' % new_list[0]
        person = self.dbsql.execsql([sql1])[0]
        print(person)
        if person != () and (person[0][1] != new_list[1] or
                             str(person[0][2]) != new_list[2] or str(person[0][3]) != new_list[3]):
            self.box.setText('与系统现有乘客信息冲突！')
            self.box.setWindowTitle('有误')
            self.box.exec_()
            return
        if person == ():
            sql1 = 'insert into person value ("%s", "%s", %s, %s);' % \
                   (new_list[0], new_list[1], new_list[2], new_list[3])
            sql2 = 'insert into agent value ( "%s",%s)' % (new_list[0], str(self.uid))
            self.dbsql.execsql([sql1, sql2])
            self.showPassenger()

    def createOrder(self, pos):
        # find out selected row
        selected_row = -1
        for i in self.fly_table.selectionModel().selection().indexes():
            selected_row = i.row()
        if selected_row == -1:
            return
        # menu match action
        menu = QMenu()
        order_1 = menu.addAction(u'下单')
        action = menu.exec_(self.fly_table.mapToGlobal(pos))
        if action != order_1:
            return
        # check money
        if self.money == 0:
            self.box.setText('余额不足，请先充值！')
            self.box.setWindowTitle('有误')
            self.box.exec_()
            return
        if self.passenger_table.rowCount() == 0:
            self.box.setText('无乘客登记，请先登记！')
            self.box.setWindowTitle('有误')
            self.box.exec_()
            return
        # select passenger
        select_n = 0
        select_name = []
        while not select_n:
            self.select_dialog = selectdialog.selectDialog(self.passenger_list)
            select_list = self.select_dialog.getData()
            self.select_dialog.close()
            for i in range(len(select_list)):
                if select_list[i]:
                    select_name.append(self.passenger_list[i])
                    select_n += 1
            if not select_n:
                self.box.setText('请选择至少一位乘客！')
                self.box.setWindowTitle('有误')
                self.box.exec_()
        # use prosedure to create order
        fname = self.fly_table.item(selected_row, 0).text()
        fdate = self.fly_table.item(selected_row, 1).text()
        ftype = self.fly_table.item(selected_row, 9).text()
        ftype_dict = {'头等舱': 1, '商务舱': 2,  '经济舱': 3}
        ftype = ftype_dict[ftype]
        sql1 = 'set @n_in_%s=%s;' % (str(self.uid), str(select_n))
        sql2 = 'call create_order((select id from flight where name="%s"), "%s", %s, %s, @n_in_%s);' % (fname, fdate, str(ftype), str(self.uid), str(self.uid))
        sql3 = 'select @n_in_%s' % str(self.uid)
        sql4 = 'select max(id) from porder for update;'
        result = self.dbsql.execsql([sql1, sql2, sql3, sql4])
        oid = result[3][0][0]
        result = result[2][0][0]
        if not result:
            self.box.setText('下单成功，请15分钟内完成支付！')
            self.box.setWindowTitle('完成')
            self.box.exec_()
            # create ticket with null passwd
            sql1 = 'insert into ticket values '
            for i in range(len(select_name)):
                sql1 += '(0,(select person.id from person,agent where agent.uid=%s and ' \
                             'agent.pid=person.id and person.name="%s"), %s, null,null,null),'\
                             % (str(self.uid), select_name[i], str(oid))
            sql1 = sql1[0:-1]+';'
            self.dbsql.execsql([sql1])
            self.timer.start(1000)
            self.showOrder()
        else:
            self.box.setText('余票不足！')
            self.box.setWindowTitle('有误')
            self.box.exec_()
    
    def showFly(self):
        # shift table
        self.tabWidget.setCurrentIndex(1)
        sql1 = 'select flight.name, fdate, off.name, land.name, flight.off_due, flight.land_due,' \
               'company.name, aircraft.name, punctual, pricef, pricec, pricey, off.code, land.code from ' \
               'fly, flight, airport off, airport land, company, aircraft where ' \
               'fly.fid=flight.id and flight.aid_f=off.id and flight.aid_t=land.id ' \
               'and flight.cid=company.id and flight.acid=aircraft.id and ' \
               'fly.id in (%s);' % str(self.fly_id)[1:-1]
        print(sql1)
        data = self.dbsql.execsql([sql1])[0]
        seat_name = ['头等舱', '商务舱', '经济舱']
        seat_price = [-5, -4, -3]
        self.fly_data = []
        for fly in data:
            temp = list(fly[0:-5])
            temp[2] = temp[2]+fly[-2]
            temp[3] = temp[3]+fly[-1]
            for i in range(len(seat_name)):
                temp1 = temp[0:]
                temp1.append(seat_name[i])
                temp1.append(fly[i-5])
                self.fly_data.append(tuple(temp1))

        self.fly_data = sorted(self.fly_data, key=lambda price: price[-1])
        self.fly_table.setRowCount(len(self.fly_data))
        for i in range(len(self.fly_data)):
            for j in range(len(self.fly_col_label)):
                self.fly_table.setItem(i, j, QTableWidgetItem(str(self.fly_data[i][j])))


    def queryRoute(self):
        aname_takeoff = self.comboBox_3.currentText()
        aname_land = self.comboBox_6.currentText()
        route_date = self.dateEdit.dateTime().toPyDateTime().date()
        if route_date.__le__(self.date):
            self.box.setText('只能查询明天以后的机票！')
            self.box.setWindowTitle('有误')
            self.box.exec_()
            return

        sql1 = 'select fly.id from fly where fdate="%s" and fid in ' \
               '(select id from flight where ' \
               'aid_f=(select id from airport where name = "%s") and ' \
               'aid_t=(select id from airport where name = "%s") and ' \
               'begin<="%s" and end>="%s")' \
               ';' % (route_date, aname_takeoff, aname_land, route_date, route_date)
        print(sql1)
        self.fly_id = []
        fly_id = self.dbsql.execsql([sql1])[0]
        for i in fly_id:
            self.fly_id.append(i[0])
        if self.fly_id == []:
            self.box.setText('没有符合要求的航班！')
            self.box.setWindowTitle('有误')
            self.box.exec_()
            return
        self.showFly()

    def showCity(self, takeoff):
        sql1 = 'select name from city where pid=(select id from province where name='
        self.city_list = []
        if takeoff:
            self.comboBox_2.clear()
            cname = self.comboBox.currentText()
            sql1 = '%s "%s");' % (sql1, cname)
            city_list = self.dbsql.execsql([sql1])[0]
            for i in city_list:
                self.city_list.append(i[0])
            self.comboBox_2.addItems(self.city_list)
        else:
            self.comboBox_5.clear()
            cname = self.comboBox_4.currentText()
            sql1 = '%s "%s");' % (sql1, cname)
            city_list = self.dbsql.execsql([sql1])[0]
            for i in city_list:
                self.city_list.append(i[0])
            self.comboBox_5.addItems(self.city_list)

    def showAirport(self, takeoff):
        sql1 = 'select name from airport where cid=(select id from city where name='
        self.airport_list = []
        if takeoff:
            self.comboBox_3.clear()
            aname = self.comboBox_2.currentText()
            sql1 = '%s "%s");' % (sql1, aname)
            airport_list = self.dbsql.execsql([sql1])[0]
            for i in airport_list:
                self.airport_list.append(i[0])
            self.comboBox_3.addItems(self.airport_list)
        else:
            self.comboBox_6.clear()
            aname = self.comboBox_5.currentText()
            sql1 = '%s "%s");' % (sql1, aname)
            airport_list = self.dbsql.execsql([sql1])[0]
            for i in airport_list:
                self.airport_list.append(i[0])
            self.comboBox_6.addItems(self.airport_list)

    def setupUi(self):
        self.setObjectName("MainWindow")
        self.resize(524, 341)
        self.centralwidget = QtWidgets.QWidget(self)

        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setGeometry(QtCore.QRect(50, 40, 411, 261))
        self.tabWidget.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.dateEdit = QtWidgets.QDateEdit(self.tab)
        self.dateEdit.setGeometry(QtCore.QRect(70, 150, 161, 22))
        self.dateEdit.setDate(self.date)
        self.dateEdit.setObjectName("dateEdit")
        self.pushButton_4 = QtWidgets.QPushButton(self.tab)
        self.pushButton_4.setGeometry(QtCore.QRect(260, 150, 81, 23))
        self.pushButton_4.setObjectName("pushButton_4")

        self.lineEdit_6 = QtWidgets.QLineEdit(self.tab)
        self.lineEdit_6.setGeometry(QtCore.QRect(70, 190, 161, 22))
        self.lineEdit_6.setObjectName("lineEdit_6")
        self.lineEdit_6.setText("请输入航班号")
        self.pushButton_5 = QtWidgets.QPushButton(self.tab)
        self.pushButton_5.setGeometry(QtCore.QRect(260, 190, 81, 23))
        self.pushButton_5.setObjectName("pushButton_5")

        self.verticalLayoutWidget_5 = QtWidgets.QWidget(self.tab)
        self.verticalLayoutWidget_5.setGeometry(QtCore.QRect(20, 20, 361, 111))
        self.verticalLayoutWidget_5.setObjectName("verticalLayoutWidget_5")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_5)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_13 = QtWidgets.QLabel(self.verticalLayoutWidget_5)
        font = QtGui.QFont()
        font.setFamily("Adobe Devanagari")
        font.setPointSize(12)
        self.label_13.setFont(font)
        self.label_13.setObjectName("label_13")
        self.horizontalLayout_2.addWidget(self.label_13)
        self.comboBox = QtWidgets.QComboBox(self.verticalLayoutWidget_5)
        self.comboBox.setObjectName("comboBox")
        self.horizontalLayout_2.addWidget(self.comboBox)
        self.comboBox_2 = QtWidgets.QComboBox(self.verticalLayoutWidget_5)
        self.comboBox_2.setObjectName("comboBox_2")
        self.horizontalLayout_2.addWidget(self.comboBox_2)
        self.comboBox_3 = QtWidgets.QComboBox(self.verticalLayoutWidget_5)
        self.comboBox_3.setObjectName("comboBox_3")
        self.horizontalLayout_2.addWidget(self.comboBox_3)
        self.verticalLayout_5.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_14 = QtWidgets.QLabel(self.verticalLayoutWidget_5)
        font = QtGui.QFont()
        font.setFamily("Adobe Devanagari")
        font.setPointSize(12)
        self.label_14.setFont(font)
        self.label_14.setObjectName("label_14")
        self.horizontalLayout_3.addWidget(self.label_14)
        self.comboBox_4 = QtWidgets.QComboBox(self.verticalLayoutWidget_5)
        self.comboBox_4.setObjectName("comboBox_4")
        self.horizontalLayout_3.addWidget(self.comboBox_4)
        self.comboBox_5 = QtWidgets.QComboBox(self.verticalLayoutWidget_5)
        self.comboBox_5.setObjectName("comboBox_5")
        self.horizontalLayout_3.addWidget(self.comboBox_5)
        self.comboBox_6 = QtWidgets.QComboBox(self.verticalLayoutWidget_5)
        self.comboBox_6.setObjectName("comboBox_6")
        self.horizontalLayout_3.addWidget(self.comboBox_6)
        self.verticalLayout_5.addLayout(self.horizontalLayout_3)
        self.tabWidget.addTab(self.tab, "")
        self.tab_5 = QtWidgets.QWidget()
        self.tab_5.setObjectName("tab_5")
        self.tabWidget.addTab(self.tab_5, "")
        self.tab_6 = QtWidgets.QWidget()
        self.tab_6.setObjectName("tab_6")
        self.tabWidget.addTab(self.tab_6, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QtWidgets.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.tabWidget.addTab(self.tab_3, "")
        self.tab_21 = QtWidgets.QWidget()
        self.tab_21.setObjectName("tab_21")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.tab_21)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(60, 20, 81, 101))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Adobe Devanagari")
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.label_2 = QtWidgets.QLabel(self.verticalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Adobe Devanagari")
        font.setPointSize(14)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.tab_21)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(140, 20, 221, 101))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.label_3 = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        font = QtGui.QFont()
        font.setFamily("Adobe Devanagari")
        font.setPointSize(14)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.verticalLayout_2.addWidget(self.label_3)
        self.label_4 = QtWidgets.QLabel(self.verticalLayoutWidget_2)
        font = QtGui.QFont()
        font.setFamily("Adobe Devanagari")
        font.setPointSize(14)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.verticalLayout_2.addWidget(self.label_4)
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.tab_21)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(80, 130, 261, 80))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_5 = QtWidgets.QLabel(self.horizontalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Adobe Devanagari")
        font.setPointSize(14)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.horizontalLayout.addWidget(self.label_5)
        self.lineEdit = QtWidgets.QLineEdit(self.horizontalLayoutWidget)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)
        self.label_6 = QtWidgets.QLabel(self.horizontalLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Adobe Devanagari")
        font.setPointSize(14)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout.addWidget(self.label_6)
        self.pushButton_2 = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.tabWidget.addTab(self.tab_21, "")
        self.tab_4 = QtWidgets.QWidget()
        self.tab_4.setObjectName("tab_4")
        self.verticalLayoutWidget_3 = QtWidgets.QWidget(self.tab_4)
        self.verticalLayoutWidget_3.setGeometry(QtCore.QRect(50, 20, 91, 171))
        self.verticalLayoutWidget_3.setObjectName("verticalLayoutWidget_3")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_3)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_7 = QtWidgets.QLabel(self.verticalLayoutWidget_3)
        font = QtGui.QFont()
        font.setFamily("Adobe Devanagari")
        font.setPointSize(12)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.verticalLayout_3.addWidget(self.label_7)
        self.label_8 = QtWidgets.QLabel(self.verticalLayoutWidget_3)
        font = QtGui.QFont()
        font.setFamily("Adobe Devanagari")
        font.setPointSize(12)
        self.label_8.setFont(font)
        self.label_8.setObjectName("label_8")
        self.verticalLayout_3.addWidget(self.label_8)
        self.label_9 = QtWidgets.QLabel(self.verticalLayoutWidget_3)
        font = QtGui.QFont()
        font.setFamily("Adobe Devanagari")
        font.setPointSize(12)
        self.label_9.setFont(font)
        self.label_9.setObjectName("label_9")
        self.verticalLayout_3.addWidget(self.label_9)
        self.label_10 = QtWidgets.QLabel(self.verticalLayoutWidget_3)
        font = QtGui.QFont()
        font.setFamily("Adobe Devanagari")
        font.setPointSize(12)
        self.label_10.setFont(font)
        self.label_10.setObjectName("label_10")
        self.verticalLayout_3.addWidget(self.label_10)
        self.verticalLayoutWidget_4 = QtWidgets.QWidget(self.tab_4)
        self.verticalLayoutWidget_4.setGeometry(QtCore.QRect(140, 10, 221, 191))
        self.verticalLayoutWidget_4.setObjectName("verticalLayoutWidget_4")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_4)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.lineEdit_3 = QtWidgets.QLineEdit(self.verticalLayoutWidget_4)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.verticalLayout_4.addWidget(self.lineEdit_3)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.verticalLayoutWidget_4)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.verticalLayout_4.addWidget(self.lineEdit_2)
        self.lineEdit_4 = QtWidgets.QLineEdit(self.verticalLayoutWidget_4)
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.verticalLayout_4.addWidget(self.lineEdit_4)
        self.lineEdit_5 = QtWidgets.QLineEdit(self.verticalLayoutWidget_4)
        self.lineEdit_5.setObjectName("lineEdit_5")
        self.verticalLayout_4.addWidget(self.lineEdit_5)
        self.pushButton_3 = QtWidgets.QPushButton(self.tab_4)
        self.pushButton_3.setGeometry(QtCore.QRect(160, 210, 75, 23))
        self.pushButton_3.setObjectName("pushButton_3")
        self.tabWidget.addTab(self.tab_4, "")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(380, 16, 55, 23))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_6 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_6.setGeometry(QtCore.QRect(320, 16, 55, 23))
        self.pushButton_6.setObjectName("pushButton_6")
        self.pushButton_7 = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton_7.setGeometry(QtCore.QRect(260, 16, 55, 23))
        self.pushButton_7.setObjectName("pushButton_7")
        self.label_11 = QtWidgets.QLabel(self.centralwidget)
        self.label_11.setGeometry(QtCore.QRect(50, 18, 58, 16))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_11.setFont(font)
        self.label_11.setObjectName("label_11")
        self.label_12 = QtWidgets.QLabel(self.centralwidget)
        self.label_12.setGeometry(QtCore.QRect(100, 18, 58, 16))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_12.setFont(font)
        self.label_12.setObjectName("label_12")
        self.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        # set statusbar
        self.label_15 = QLabel()
        self.label_15.setText('今日  ' + str(self.date))
        self.statusbar.addPermanentWidget(self.label_15)

        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "乘客用户：航班票务系统"))
        self.pushButton_4.setText(_translate("MainWindow", "查询行程"))
        self.pushButton_5.setText(_translate("MainWindow", "查询航班号"))
        self.label_13.setText(_translate("MainWindow", "       出发"))
        self.label_14.setText(_translate("MainWindow", "       到达"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("MainWindow", "查询"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_5), _translate("MainWindow", "航班"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "订单"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("MainWindow", "乘客"))
        self.label.setText(_translate("MainWindow", "银行卡："))
        self.label_2.setText(_translate("MainWindow", "充值金："))
        self.label_3.setText(_translate("MainWindow", "无"))
        self.label_4.setText(_translate("MainWindow", "0"))
        self.label_5.setText(_translate("MainWindow", "充值"))
        self.label_6.setText(_translate("MainWindow", "RMB"))
        self.pushButton_2.setText(_translate("MainWindow", "PushButton"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_21), _translate("MainWindow", "充值"))
        self.label_7.setText(_translate("MainWindow", "           机场："))
        self.label_8.setText(_translate("MainWindow", "           航司："))
        self.label_9.setText(_translate("MainWindow", "身份证号："))
        self.label_10.setText(_translate("MainWindow", "取票密码："))
        self.pushButton_3.setText(_translate("MainWindow", "取票"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), _translate("MainWindow", "值机"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_6), _translate("MainWindow", "机票"))
        self.pushButton.setText(_translate("MainWindow", "退出"))
        self.pushButton_6.setText(_translate("MainWindow", "新增乘客"))
        self.pushButton_7.setText(_translate("MainWindow", "修改密码"))
        self.pushButton_2.setText(_translate("MainWindow", "确认"))
        self.label_11.setText(_translate("MainWindow", "Hello, "))
        self.label_12.setText(_translate("MainWindow", self.uname))

        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(self)

        province_list = self.dbsql.execsql(['select name from province order by name;'])[0]
        for i in province_list:
            self.province_list.append(i[0])
        self.comboBox.addItems(self.province_list)
        self.comboBox_4.addItems(self.province_list)
        self.showCity(True)
        self.showCity(False)
        self.showAirport(True)
        self.showAirport(False)


