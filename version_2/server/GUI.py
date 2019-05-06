import sys
from PyQt5.QtCore import QT_TR_NOOP, QTranslator
from PyQt5 import QtGui, QtWidgets, uic
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QWidget, QMainWindow, QMessageBox, QApplication

import SERVER_model

class GUI(QMainWindow):
    def __init__(self, parent=None):
        super(GUI, self).__init__(parent)

        self.modes = [SERVER_model.Server_sync, SERVER_model.All_sync, SERVER_model.All_to_All]

        uic.loadUi("SERVER_GUI.ui", self)

        self.show()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = GUI()
    sys.exit(app.exec())
