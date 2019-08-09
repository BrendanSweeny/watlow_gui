import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QSize
from controller_ui import Ui_Form
from watlow import PM3

class ControllerWidget(QWidget):

    widgetEmitted = pyqtSignal(object)

    def __init__(self, connection, name='No Name', address=None, mode=None):
        super().__init__()

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.connection = connection
        self.name = name
        self.address = int(address)
        self.mode = mode

        self.ui.labelName.setText(self.name)
        self.ui.labelAddress.setText(str(self.address))
        self.ui.cbMode.addItems(['Off', 'Heat', 'Cool'])
        if mode.lower() == 'cool':
            self.ui.cbMode.setCurrentIndex(2)
        elif mode.lower() == 'heat':
            self.ui.cbMode.setCurrentIndex(1)

        self.controller = PM3(self.connection, address=self.address)

        self.ui.btnSetTemp.clicked.connect(self.handleSetTemp)
        self.ui.btnDelete.clicked.connect(self.handleEmitWidget)

    def handleEmitWidget(self):
        self.widgetEmitted.emit(self)

    def handleSetTemp(self):
        try:
            tempK = int(self.ui.leSetTemp.text())
        except Exception as e:
            print(e)
        else:
            self.write('setpoint', self._k_to_c(tempK))

    # sizeHint and minimumSizeHint functions from QWidget-derived custom widgets
    # return QSize(-1, -1).
    # Meaning it will shrink to zero when added to a layout as in control_tab.py
    # These sizes are from the controller_ui.ui file
    def sizeHint(self):
        return QSize(489, 84)

    def minimumSizeHint(self):
        return QSize(489, 84)

    def _k_to_c(self, k):
        return k - 273.15

    def _c_to_k(self, c):
        return c + 273.15

    def read(self, command):
        commandDict = {'currentTemp': '4001', 'setpoint': '7001'}
        response = self.controller.write(dataParam=commandDict[command])
        print(response)
        try:
            if command == 'currentTemp':
                self.ui.lcdCurrentT.display(self._c_to_k(response['data']))
            elif command == 'setpoint':
                self.ui.lcdSetpoint.display(self._c_to_k(response['data']))
        except Exception as e:
            print(e)
        if not response['error']:
            self.ui.connectLED.changeState(True)
        else:
            self.ui.connectLED.changeState(False)

    def updateSerial(self, serialObj):
        self.controller.updateSerial(serialObj)

    def write(self, command, value):
        if command == 'setpoint':
            response = self.controller.set(value)
            try:
                self.ui.lcdSetpoint.display(self._c_to_k(response['data']))
            except Exception as e:
                print(e)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ControllerWidget()
    window.show()
    sys.exit(app.exec_())
