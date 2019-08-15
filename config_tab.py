import sys
import configparser
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QFileDialog
from PyQt5.QtCore import pyqtSignal
from config_tab_ui import Ui_Form

class ConfigTabWidget(QWidget):

    fnameEmitted = pyqtSignal(str)
    tabIndexEmitted = pyqtSignal(int)
    manualAddEmitted = pyqtSignal(object)

    def __init__(self):
        super().__init__()

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.ui.btnOpenConfig.clicked.connect(self._handleOpenConfig)

        self.ui.cbMode.addItem('Heat')
        self.ui.cbMode.addItem('Cool')

        self.ui.btnAdd.clicked.connect(self._manualAdd)

    def _handleOpenConfig(self):
        fileName = QFileDialog.getOpenFileName(self, 'Open File', filter='*.ini')
        if fileName[0]:
            self.fnameEmitted.emit(fileName[0])
            # Change to control tab:
            self.tabIndexEmitted.emit(0)

    def _manualAdd(self):
        name = self.ui.leName.text()
        address = int(self.ui.leAddress.text())
        modeIndex = self.ui.cbMode.currentIndex()
        mode = self.ui.cbMode.itemText(modeIndex).lower()
        self.manualAddEmitted.emit((name, address, mode))
        self.ui.leName.clear()
        self.ui.leAddress.clear()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ConfigTabWidget()
    window.show()
    sys.exit(app.exec_())
