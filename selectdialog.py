from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys

class selectDialog(QDialog):
    def __init__(self, label_list, parent=None):
        super(selectDialog, self).__init__(parent)
        self.new_list = []
        self.lb_list = []
        self.cb_list = []
        layout = QFormLayout()

        for i in range(len(label_list)):
            self.lb_list.append(QLabel(label_list[i]))
            self.cb_list.append(QCheckBox())
            layout.addRow(self.cb_list[i], self.lb_list[i])
        self.btn1 = QPushButton('确认')
        self.btn2 = QPushButton('取消')
        self.btn1.clicked.connect(self.comfirm)
        self.btn2.clicked.connect(self.accept)
        layout.addRow(self.btn1, self.btn2)

        self.setLayout(layout)
        self.setWindowTitle('多选')
        self.exec_()

    def comfirm(self):
        for i in range(len(self.lb_list)):
            self.new_list.append(self.cb_list[i].checkState())
        self.hide()

    def getData(self):
        return self.new_list

# if __name__ == '__main__':
#     app=QApplication(sys.argv)
#     demo=selectDialog(['wly', 'hls', 'hsz'])
#     demo.show()
#     demo.getData()
#     demo.reject()
#     sys.exit(app.exec_())