import sys
from PyQt5.QtCore import QT_TR_NOOP, QTranslator
from PyQt5 import QtGui, QtWidgets, uic
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QWidget, QMainWindow, QMessageBox, QApplication
from PyQt5.QtGui import QIntValidator, QRegularExpressionValidator
import re

import SERVER_model

class GUI(QMainWindow):
    def __init__(self, parent=None):
        super(GUI, self).__init__(parent)

        uic.loadUi("SERVER_GUI.ui", self)

        self.modes = [SERVER_model.Server_sync, SERVER_model.All_sync, self.ata_mod]
        self.mode_box.addItems(["server", "all", "All_to_All"])
        self.port_input.setValidator(QIntValidator())
        self.start_btn.clicked.connect(self.key)

        self.lw = QtWidgets.QListView(self)
        self.refresh_btn = QtWidgets.QPushButton("R",self)
        self.get_btn = QtWidgets.QPushButton("Get clip",self)

        self.lw.setGeometry(250,10,210,140)
        self.refresh_btn.setGeometry(420,200,50,27)
        self.get_btn.setGeometry(250,200,150,27)

        self.lw.show()
        self.refresh_btn.show()
        self.get_btn.show()

        self.show()
    def key(self):
        if hasattr(self, "model"):
            print(self.model)
            self.nickname_input.setEnabled(True)
            self.port_input.setEnabled(True)
            self.mode_box.setEnabled(True)
            self.resize(230, 280)
            self.model.destroy()
            delattr(self, "model")
            self.start_btn.setText("Start server")
        else:
            self.nickname_input.setEnabled(False)
            self.port_input.setEnabled(False)
            self.mode_box.setEnabled(False)
            # self.nickname_input.setEnabled(False)
            nick = self.nickname_input.text()
            port = int(self.port_input.text())
            # ip = self.ip_input.text()
            self.model = self.modes[self.mode_box.currentIndex()](nickname=nick,port=port)
            self.start_btn.setText("Stop server")

    def ata_mod(self,nickname,port):


        self.resize(500, 280)

        return SERVER_model.All_to_All(nickname=nickname,port=port)



    def closeEvent(self, ev):
        if hasattr(self, "model"):
            self.model.destroy()
        ev.accept()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = GUI()
    sys.exit(app.exec())
