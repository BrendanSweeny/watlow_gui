import sys
import configparser
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QFileDialog
from PyQt5.QtCore import pyqtSignal
from config_tab_ui import Ui_Form

class ConfigTabWidget(QWidget):

    fnameEmitted = pyqtSignal(str)
    tabIndexEmitted = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.ui.btnOpenConfig.clicked.connect(self.handleOpenConfig)

    def handleOpenConfig(self):
        fileName = QFileDialog.getOpenFileName(self, 'Open File', filter='*.ini')
        #self.parseConfigFile(fileName)
        if fileName[0]:
            self.fnameEmitted.emit(fileName[0])
            # Change to control tab:
            self.tabIndexEmitted.emit(0)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ConfigTabWidget()
    window.show()
    sys.exit(app.exec_())
