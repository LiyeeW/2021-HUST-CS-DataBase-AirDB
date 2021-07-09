import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog
from functools import partial


import ui_welcome
import welcome





# def myslot(str):
#      str = ui.lineEdit.text()
#      print(str)
#      ui.pushButton.setText(str)


if __name__ == '__main__':
     app = QApplication(sys.argv)
     Dialog = QDialog()
     my_welcome = welcome.welcome(Dialog)
     Dialog.show()


     # ui.pushButton.clicked.connect(partial(myslot, "1"))

     sys.exit(app.exec_())