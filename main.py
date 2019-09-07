import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon
from main_ui import Ui_MainWindow
from control_tab import ControlTabWidget
from config_tab import ConfigTabWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setWindowTitle('Watlow EZ-Zone PM3 Temperature Control')
        # Icon from: https://icons8.com/icons/set/temperature
        self.setWindowIcon(QIcon('icon.png'))

        # Tab and Widget Setup
        self.controlTabWidget = ControlTabWidget()
        self.configTabWidget = ConfigTabWidget()
        self.ui.tabWidget.insertTab(0, self.controlTabWidget, 'Control')
        self.ui.tabWidget.insertTab(1, self.configTabWidget, 'Config')
        #self.ui.tabWidget.insertTab(1, self.massSpecWidget, 'Mass Spec Plot')

        self.configTabWidget.fnameEmitted.connect(self.controlTabWidget.parseConfigFile)
        self.controlTabWidget.statusEmitted.connect(self._displayStatus)
        self.configTabWidget.tabIndexEmitted.connect(self._changeTab)
        self.configTabWidget.manualAddEmitted.connect(self.controlTabWidget.handleManualAdd)

    def _displayStatus(self, message):
        self.ui.statusbar.showMessage(message, 10000)

    def _changeTab(self, index):
        self.ui.tabWidget.setCurrentIndex(index)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
