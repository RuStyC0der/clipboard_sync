import sys
from PyQt5.QtCore import QT_TR_NOOP, QTranslator, QRegularExpression
from PyQt5 import QtGui, QtWidgets, uic
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QWidget, QMainWindow, QMessageBox, QApplication
from PyQt5.QtGui import QIntValidator, QRegularExpressionValidator
import CLIENT_model

import CLIENT_model



class GUI(QMainWindow):
    def __init__(self, parent=None):
        super(GUI, self).__init__(parent)

        uic.loadUi("CLIENT_GUI.ui", self)

        self.modes = [CLIENT_model.Server_sync, CLIENT_model.All_sync, CLIENT_model.All_to_All]
        self.mode_box.addItems(["server", "all", "All_to_All"])
        self.port_input.setValidator(QIntValidator())
        self.ip_input.setValidator(QRegularExpressionValidator(QRegularExpression(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')))
        self.connect_btn.clicked.connect(self.key)


        self.show()

    def key(self):
        if hasattr(self, "model"):
            self.nickname_input.setEnabled(True)
            self.port_input.setEnabled(True)
            self.mode_box.setEnabled(True)
            self.ip_input.setEnabled(True)

            self.model.destroy()
            delattr(self, "model")
            self.start_btn.setText("Start server")
        else:
            self.nickname_input.setEnabled(False)
            self.port_input.setEnabled(False)
            self.mode_box.setEnabled(False)
            self.ip_input.setEnabled(False)
            nick = self.nickname_input.text()
            port = int(self.port_input.text())
            ip = self.ip_input.text()
            self.model = self.modes[self.mode_box.currentIndex()](nickname=nick,port=port, ip=ip)
            self.start_btn.setText("Stop server")

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = GUI()
    sys.exit(app.exec())
