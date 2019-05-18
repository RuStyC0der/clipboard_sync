import sys
from PyQt5.QtCore import QRegularExpression
from PyQt5 import QtGui, QtWidgets, uic
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtGui import QIntValidator, QRegularExpressionValidator

import CLIENT_model
from time import sleep



class GUI(QMainWindow):
    def __init__(self, parent=None):
        super(GUI, self).__init__(parent)

        uic.loadUi("CLIENT_GUI.ui", self)
        self.setWindowTitle("Client")

        self.modes = [CLIENT_model.Server_sync, CLIENT_model.All_sync, self.ata_mod]
        self.mode_box.addItems(["server", "all", "All_to_All"])
        self.port_input.setValidator(QIntValidator())
        self.ip_input.setValidator(QRegularExpressionValidator(QRegularExpression(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')))
        self.connect_btn.clicked.connect(self.key)
        self.actionquit.triggered.connect(self.close)

        self.lw = QtWidgets.QListWidget(self)
        self.refresh_btn = QtWidgets.QPushButton("R",self)
        self.get_btn = QtWidgets.QPushButton("Get clip",self)

        self.lw.setGeometry(250,10,210,140)
        self.refresh_btn.setGeometry(420,200,50,27)
        self.get_btn.setGeometry(250,200,150,27)


        self.lw.show()
        self.refresh_btn.show()
        self.get_btn.show()

        self.refresh_btn.clicked.connect(self.refresh)
        self.get_btn.clicked.connect(self.get_clip)

        self.setFixedSize(self.width(), self.height())

        self.show()

    def key(self):
        if hasattr(self, "model"):
            self.nickname_input.setEnabled(True)
            self.port_input.setEnabled(True)
            self.mode_box.setEnabled(True)
            self.ip_input.setEnabled(True)
            self.resize(230, 280)
            self.model.destroy()
            delattr(self, "model")
            self.connect_btn.setText("Start server")
        else:

            nick = self.nickname_input.text()
            port = self.port_input.text()
            ip = self.ip_input.text()
            if not port or not ip or not nick:
                self.statusBar().showMessage("input error")
                return
            try:
                self.model = self.modes[self.mode_box.currentIndex()](nickname=nick,port=int(port), ip=ip)
                self.statusBar().showMessage("sucess connected")
            except Exception as e:
                self.statusBar().showMessage(str(e))
                return

            self.connect_btn.setText("Disconnect")
            self.nickname_input.setEnabled(False)
            self.port_input.setEnabled(False)
            self.mode_box.setEnabled(False)
            self.ip_input.setEnabled(False)



    def ata_mod(self,nickname,port, ip):


        self.resize(500, 280)

        return CLIENT_model.All_to_All(ip=ip, nickname=nickname,port=port)


    def refresh(self):
        self.model.refresh_user_list()
        sleep(0.5)
        self.lw.clear()
        self.lw.addItems(list(self.model.user_list.keys()))

    def get_clip(self):
        user = self.lw.currentItem()
        self.model.get_usr_clip(user)

    def closeEvent(self, ev):
        if hasattr(self, "model"):
            self.model.destroy()
        ev.accept()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = GUI()
    sys.exit(app.exec())
