import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QPushButton
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QSize
from controller_ui import Ui_Form
from watlow_driver import PM3

class ControllerWidget(QWidget):

    widgetEmitted = pyqtSignal(object)
    statusEmitted = pyqtSignal(str)
    setPointEmitted = pyqtSignal(object)

    def __init__(self, connection, name='No Name', address=None, mode=None, maxTemp=None):
        super().__init__()

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.connection = connection
        self.name = name
        self.address = int(address)
        self.mode = mode
        self.maxTemp = maxTemp

        self.setpoint = 0

        # Setup scrollArea entry information:
        self.ui.labelName.setText(self.name)
        self.ui.labelAddress.setText(str(self.address))
        self.ui.cbMode.addItems(['Off', 'Heat', 'Cool'])
        if mode.lower() == 'cool':
            self.ui.cbMode.setCurrentIndex(2)
        elif mode.lower() == 'heat':
            self.ui.cbMode.setCurrentIndex(1)

        # Initiate instance of Watlow PM3 Controller:
        self.controller = PM3(self.connection, address=self.address)

        # Signals/Slots:
        #self.ui.btnSetTemp.clicked.connect(self._handleSetTemp)
        self.ui.btnSetTemp.clicked.connect(self._emitSetTemp)
        self.ui.btnDelete.clicked.connect(self._handleEmitWidget)
        #self.ui.leSetTemp.returnPressed.connect(self._handleSetTemp)
        self.ui.leSetTemp.returnPressed.connect(self._emitSetTemp)
        self.ui.cbMode.currentTextChanged.connect(self._handleChangeMode)

    def _handleEmitWidget(self):
        self.widgetEmitted.emit(self)

    def _emitSetTemp(self):
        self.setPointEmitted.emit(self._handleSetTemp)

    def _handleSetTemp(self):
        try:
            tempK = int(self.ui.leSetTemp.text())
            if self.maxTemp and tempK > self.maxTemp:
                self.statusEmitted.emit('Setpoint exceeds max temperature!')
            else:
                self.write('setpoint', self._k_to_c(tempK))
        except Exception as e:
            print('_handleSetTemp: ', e)
        #self.ui.leSetTemp.clear()

    def _handleChangeMode(self, value):
        self.mode = value.lower()

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

    def _handleResponse(self, command, response):
        if response['error']:
            print(response['error'])
            return
        if command == 'currentTemp':
            self.ui.lcdCurrentT.display(self._c_to_k(response['data']))
            # Status LED:
            if abs((self._c_to_k(response['data']) - self.setpoint)) < 20:
                self.ui.connectLED.changeState(True)
            else:
                self.ui.connectLED.changeState(False)
        elif command == 'setpoint':
            self.ui.lcdSetpoint.display(self._c_to_k(response['data']))
            self.setpoint = self._c_to_k(response['data'])
        return

    def updateSerial(self, serialObj):
        self.controller.updateSerial(serialObj)

    def read(self, command):
        commandDict = {'currentTemp': '4001', 'setpoint': '7001'}
        try:
            response = self.controller.write(dataParam=commandDict[command])
        except Exception as e:
            print(e)
        else:
            #print(response)
            self._handleResponse(command, response)

    def write(self, command, value):
        try:
            response = self.controller.set(value)
        except Exception as e:
            print(e)
        else:
            self._handleResponse(command, response)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ControllerWidget()
    window.show()
    sys.exit(app.exec_())
