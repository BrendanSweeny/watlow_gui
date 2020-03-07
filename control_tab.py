# TODO: Offload controller timer read interval to config file (with an internal default)
# TODO: Consider changing the controller LCDs to a label or something more visually appealing
# TODO: Display the config parameters or default parameters somehow, likely means moving parsing to config_tab and emitting a dictionary??

import sys
import configparser
import serial
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QVBoxLayout, QPushButton, QButtonGroup
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import pyqtSignal, QTimer, QThreadPool, QObject
from PyQt5.Qt import *
from control_tab_ui import Ui_Form
from controller import ControllerWidget
from led import LEDWidget
from worker import Worker

class ControlTabWidget(QWidget):

    serialObjectEmitted = pyqtSignal(str)
    statusEmitted = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.serial = serial.Serial()

        self.controllerWidgets = None

        # Default maximum setpoint temperature in kelvin:
        self.maxTemp = 800

        # Dictionary that contains controllerWidgets by address/object key/val pairs
        self.controllerWidgetsDict = {}

        # Timer that handles blinking LED
        self.ledTimer = QTimer(self)
        self.ledTimer.timeout.connect(self._handleBlinkLED)

        # Threadpool to handle concurrent tasks (periodic controller reads):
        # * The threadpool handles all Watlow read/set requests to prevent blocking.
        # * The threadpool is limited to one thread so that requests and reads remain
        #   sequential even when a set request is triggered during a periodic read.
        #   Otherwise it is possible to read responses out of order.
        self.threadpool = QThreadPool()
        self.threadpool.setMaxThreadCount(1)

        # Timer that reads controller values at specified interval
        self.readTimer = QTimer(self)
        self.readTimer.timeout.connect(lambda: self._runInThreadpool(self._readTempAll))

        # Default temperature and setpoint read interval in milliseconds:
        self.readInterval = 60000

        # Sets up the scroll widget to have vertical box layout for controllers:
        self.scrollWidget = QWidget()
        self.scrollWidgetLayout = QVBoxLayout()
        self.scrollWidgetLayout.setAlignment(Qt.AlignTop)
        self.scrollWidget.setLayout(self.scrollWidgetLayout)
        self.ui.scrollArea.setWidget(self.scrollWidget)

        # Available serial ports and descriptions
        self.availablePorts = None
        self._populateSerialPorts()

        # Button group is used primarily for 'exclusive' checked behavior
        self.tempButtons = QButtonGroup()
        self.tempButtons.setExclusive(False)
        self.tempButtons.addButton(self.ui.btn100K)
        self.tempButtons.addButton(self.ui.btn200K)
        self.tempButtons.addButton(self.ui.btn400K)
        self.tempButtons.addButton(self.ui.btn500K)
        self.tempButtons.addButton(self.ui.btn600K)
        self.tempButtons.addButton(self.ui.btn700K)

        # Signals and Slots:
        self.ui.btnSerialConnect.clicked.connect(self._toggleConnect)
        self.ui.btnRefreshPorts.clicked.connect(self._populateSerialPorts)
        self.ui.btnSetCustomTemp.clicked.connect(self._setCustomTempAll)
        self.ui.leSetCustomTemp.returnPressed.connect(self._setCustomTempAll)

        # Temperature set buttons:
        for btn in self.tempButtons.buttons():
            btn.clicked.connect(lambda: self.buttonGroupSetTempAll())

    def _clearLayout(self):
        for i in reversed(range(self.scrollWidgetLayout.count())):
            self.scrollWidgetLayout.itemAt(i).widget().setParent(None)

    def _deleteWidget(self, widget):
        '''
        Deletes a single widget from the control_tab (used with controllers'
        'delete' button). A widget is deleted when its parent is removed as
        opposed to deleteLater() where the layout may still contain the widget
        '''
        widget.setParent(None)
        del self.controllerWidgetsDict[widget.address]

    def _setCustomTempAll(self):
        '''
        Handles behavior of the custom temperature line edit
        '''
        try:
            tempK = self.ui.leSetCustomTemp.text()
            tempK = int(tempK)
        except ValueError as e:
            print(e)
            self.statusEmitted.emit('Temperature must be an integer.')
        else:
            if self.maxTemp and tempK > self.maxTemp:
                self.statusEmitted.emit('Setpoint exceeds max temperature!')
            else:
                self._handleSetTempAll(tempK)
            for btn in self.tempButtons.buttons():
                btn.setStyleSheet('')
        finally:
            self.ui.leSetCustomTemp.clear()

    def _k_to_c(self, k):
        return k - 273.15

    def _setTempAll(self, temp):
        '''
        Sets temperature of connected watlow controllers based on
        specified heat/cool mode
        '''
        for address, controllerWidget in self.controllerWidgetsDict.items():
            if controllerWidget.mode == 'heat' and temp > 25:
                controllerWidget.write('setpoint', temp)
            elif controllerWidget.mode == 'cool' and temp < 25:
                controllerWidget.write('setpoint', temp)

    def buttonGroupSetTempAll(self):
        if not self.serial.isOpen() or not self.serial:
            self.statusEmitted.emit('Serial port is not open!')
        else:
            clickedBtn = self.sender()
            tempK = int(clickedBtn.text().split(' ')[0])
            self._handleSetTempAll(tempK)

            # Colors selected button based on temperature:
            for btn in self.tempButtons.buttons():
                if btn == clickedBtn and tempK > 300:
                    btn.setStyleSheet('QPushButton {background-color: "red"}')
                elif btn == clickedBtn and tempK < 300:
                    btn.setStyleSheet('QPushButton {background-color: "blue"; color: "white"}')
                else:
                    btn.setStyleSheet('')

    def _handleSetTempAll(self, tempK=None):
        '''
        Creates a worker to run the _setTempAll fn on a seperate thread.
        Running on a seperate thread is probably not as necessary as _readTempAll
        since it's run once per setpoint change

        * Attempts to extract temperature from the button text value if not
          passed as an argument (assumes kelvin)
        '''
        if self.maxTemp and tempK > self.maxTemp:
            self.statusEmitted.emit('Setpoint exceeds max temperature!')
        else:
            tempC = self._k_to_c(tempK)
            self._runInThreadpool(self._setTempAll, tempC)

    def _readTempAll(self):
        '''
        Reads current temp and setpoint for all controllers
        '''
        for address, controllerWidget in self.controllerWidgetsDict.items():
            controllerWidget.read('currentTemp')
            controllerWidget.read('setpoint')

    def _toggleTimerRead(self):
        '''
        Initiates the QTimer for the read queries (_readTempAll)
        '''
        if not self.readTimer.isActive():
            self.readTimer.start(self.readInterval)
            self._runInThreadpool(self._readTempAll)
        elif self.readTimer.isActive():
            self.readTimer.stop()

    def _handleBlinkLED(self):
        if self.ui.monitorLED.state:
            self.ui.monitorLED.changeState(False)
        else:
            self.ui.monitorLED.changeState(True)

    def _toggleBlinkLED(self):
        '''
        Starts/Stops blinking LED used to indicate that serial is open and
        periodic read QTimer is running
        '''
        if not self.ledTimer.isActive():
            self.ledTimer.start(1000)
            self._handleBlinkLED()
        elif self.ledTimer.isActive():
            self.ledTimer.stop()

    def _populateSerialPorts(self):
        '''
        Finds all connected serial ports and populates the serial combo box
        with the name and description of each
        '''
        portList = QSerialPortInfo.availablePorts()
        self.ui.cbSerial.clear()
        self.ui.cbSerial.addItem('Select a port')
        outputList = ['']
        for port in portList:
            name = port.portName()
            description = '(no description)'
            if port.description:
                description = port.description()
            print(name, description)
            line = name + ', ' + description

            self.ui.cbSerial.addItem(line)
            outputList.append(name)
        self.availablePorts = outputList

    def _toggleConnect(self):
        '''
        Toggles connection to the serial port selected with the serial combo box
        and handles initial program behavior:

        * Sends connect/disconnect message
        * Changes connect button text
        * Changes/blinks LEDs
        * Toggles the read timer
        '''
        index = self.ui.cbSerial.currentIndex()
        if index == 0:
            self.statusEmitted.emit('Please select a port.')
        elif not self.serial.isOpen() or not self.serial:
            print(self.availablePorts, self.availablePorts[index])
            self.serial.port = self.availablePorts[index]
            self.serial.baudrate = 38400 # Watlow controller default baudrate
            self.serial.timeout = 0.5
            try:
                self.serial.open()
            except serial.SerialException as e:
                print(e)
                self.statusEmitted.emit('Could not open port: ' + self.availablePorts[index])
            else:
                if self.controllerWidgetsDict:
                    for address, controllerWidget in self.controllerWidgetsDict.items():
                        controllerWidget.updateSerial(self.serial)
                self.ui.btnSerialConnect.setText('Disconnect')
                self.ui.connectLED.changeState(True)
                self.statusEmitted.emit('Connected to {0}'.format(self.serial.port))
                self._toggleTimerRead()
                self._toggleBlinkLED()
        else:
            self._toggleTimerRead()
            self._toggleBlinkLED()
            self.ui.monitorLED.changeState(False)
            self.serial.flush()
            self.serial.close()
            self.ui.btnSerialConnect.setText('Connect')
            self.ui.connectLED.changeState(False)
            for address, controller in self.controllerWidgetsDict.items():
                controller.ui.connectLED.changeState(False)
            self.statusEmitted.emit('Disconnected from {0}'.format(self.serial.port))
            for btn in self.tempButtons.buttons():
                btn.setStyleSheet('')

    def _passStatus(self, statusStr):
        '''Emits string to main.py to be shown in the status bar'''
        self.statusEmitted.emit(statusStr)

    def parseConfigFile(self, fileName):
        '''
        Handler for config file name emitted from config_tab widget
        '''
        config = configparser.ConfigParser()
        config.read(fileName)
        serialSettings = config['SERIAL']

        if 'maxtemp' in config['GENERAL'].keys():
            self.maxTemp = float(config['GENERAL']['maxtemp'])
        else:
            self.maxTemp = 800
        if 'readinterval' in config['GENERAL'].keys():
            self.readInterval = int(config['GENERAL']['readinterval']) * 1000
        else:
            self.readInterval = 60000

        # Extract Serial Info:
        try:
            self.port = config['SERIAL']['port']
            self.baudrate = config['SERIAL']['baudrate']
            self.timeout = config['SERIAL']['timeout']

            for i, availablePort in enumerate(self.availablePorts):
                if self.port in availablePort:
                    self.ui.cbSerial.setCurrentIndex(i)
        except Exception as e:
            print(e)
        else:
            print(self.port, self.baudrate, self.timeout)

        # Deal with Controller Info:
        try:
            reservedNames = ['SERIAL', 'GENERAL']
            controllers = [controller for controller in config.sections() if controller not in reservedNames]
            if controllers == []:
                raise Exception('No controllers found in config file.')
        except Exception as e:
            print(e)
        else:
            self.controllerWidgetsDict = {int(config[controller]['address']): ControllerWidget(self.serial, controller.title(), int(config[controller]['address']), config[controller]['mode'], self.maxTemp) for controller in controllers}
            self._clearLayout()
            for address, controllerWidget in self.controllerWidgetsDict.items():
                self.scrollWidgetLayout.addWidget(controllerWidget)
                controllerWidget.widgetEmitted.connect(self._deleteWidget)
                controllerWidget.statusEmitted.connect(self._passStatus)
                controllerWidget.setPointEmitted.connect(self._runInThreadpool)

        if self.serial.isOpen():
            # Toggles read timer off then on again (reads when toggled on)
            self._toggleTimerRead()
            self._toggleTimerRead()

    def _runInThreadpool(self, func, *args, **kwargs):
        '''
        Creates QRunnable and passes to threadpool. Used with:
        * Periodic temp/setpoint reads
        * Changing setpoints from the control tab
        * Individual set requests emitted from controller instances
        '''
        self.threadpool.start(Worker(func, *args, **kwargs))

    def handleManualAdd(self, controllerInfo):
        '''
        Slot used to add a controller manually from the config tab
        '''
        name = controllerInfo[0]
        address = controllerInfo[1]
        mode = controllerInfo[2]
        controllerWidget = ControllerWidget(self.serial, name, address, mode)
        self.controllerWidgetsDict[address] = controllerWidget
        self.scrollWidgetLayout.addWidget(controllerWidget)
        controllerWidget.widgetEmitted.connect(self._deleteWidget)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ControlTabWidget()
    window.show()
    sys.exit(app.exec_())
