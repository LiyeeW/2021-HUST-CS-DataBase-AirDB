from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys

class inputDialog(QDialog):
    def __init__(self, label_list, old_list, parent=None):
        super(inputDialog, self).__init__(parent)
        self.old_list = old_list
        self.new_list = []
        self.lb_list = []
        self.le_list = []
        layout = QFormLayout()

        for i in range(len(label_list)):
            self.lb_list.append(QLabel(label_list[i]))
            self.le_list.append(QLineEdit())
            self.le_list[i].setText(old_list[i])
            layout.addRow(self.lb_list[i], self.le_list[i])
        self.btn1 = QPushButton('确认')
        self.btn2 = QPushButton('取消')
        self.btn1.clicked.connect(self.comfirm)
        self.btn2.clicked.connect(self.accept)
        layout.addRow(self.btn1, self.btn2)

        self.setLayout(layout)
        self.setWindowTitle('增改')
        self.exec_()

    def comfirm(self):
        for i in range(len(self.old_list)):
            self.new_list.append(self.le_list[i].text())
        self.hide()

    def getData(self):
        return self.new_list

# if __name__ == '__main__':
#     app=QApplication(sys.argv)
#     demo=inputDialog(['省份'], ['湖北'])
#     demo.show()
#     sys.exit(app.exec_())