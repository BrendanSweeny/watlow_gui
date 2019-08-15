import sys
import configparser
import serial
from PyQt5.QtWidgets import QApplication, QWidget, QLineEdit, QVBoxLayout, QPushButton
from PyQt5.QtSerialPort import QSerialPort, QSerialPortInfo
from PyQt5.QtCore import pyqtSignal, QIODevice, QTimer, QRunnable, QThreadPool, QObject
from PyQt5.Qt import *
from control_tab_ui import Ui_Form
from controller import ControllerWidget
from led import LEDWidget

class Worker(QRunnable):
    '''
    Runnable "worker" used to execute functions on a seperate thread than
    the PyQt event loop
    '''
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        try:
            self.func(*self.args, **self.kwargs)
        except Exception as e:
            print(e)

class ControlTabWidget(QWidget):

    serialObjectEmitted = pyqtSignal(str)
    statusEmitted = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.serial = serial.Serial()

        self.controllerWidgets = None

        # Dictionary that contains controllerWidgets by address/object key/val pairs
        self.controllerWidgetsDict = {}

        # Timer that reads controller values at specified interval
        self.readTimer = QTimer(self)
        self.readTimer.timeout.connect(self._handleTimerRead)

        # Timer that handles blinking LED
        self.ledTimer = QTimer(self)
        self.ledTimer.timeout.connect(self._handleBlinkLED)

        # Threadpool to handle concurrent tasks (periodic controller reads):
        self.threadpool = QThreadPool()

        # Sets up the scroll widget to have vertical box layout for controllers:
        self.scrollWidget = QWidget()
        self.scrollWidgetLayout = QVBoxLayout()
        self.scrollWidgetLayout.setAlignment(Qt.AlignTop)
        self.scrollWidget.setLayout(self.scrollWidgetLayout)
        self.ui.scrollArea.setWidget(self.scrollWidget)

        # Available serial ports and descriptions
        self.availablePorts = None
        self._populateSerialPorts()

        # Signals and Slots:
        self.ui.btnSerialConnect.clicked.connect(self._toggleConnect)
        self.ui.btnRefreshPorts.clicked.connect(self._populateSerialPorts)
        self.ui.btnSetCustomTemp.clicked.connect(self._setCustomTempAll)
        self.ui.leSetCustomTemp.returnPressed.connect(self._setCustomTempAll)

        # Temperature set buttons:
        self.ui.btn100K.clicked.connect(lambda: self._handleSetTempAll(100))
        self.ui.btn200K.clicked.connect(lambda: self._handleSetTempAll(200))
        self.ui.btn400K.clicked.connect(lambda: self._handleSetTempAll(400))
        self.ui.btn500K.clicked.connect(lambda: self._handleSetTempAll(500))
        self.ui.btn600K.clicked.connect(lambda: self._handleSetTempAll(600))
        self.ui.btn700K.clicked.connect(lambda: self._handleSetTempAll(700))

    def _clearLayout(self):
        for i in reversed(range(self.scrollWidgetLayout.count())):
            self.scrollWidgetLayout.itemAt(i).widget().setParent(None)

    def _deleteWidget(self, widget):
        '''
        Deletes a single widget from the control_tab (used with controllers'
        'delete' button)
        '''
        # Delete from layout:
        # It appears that a widget is deleted when its parent is removed
        # As opposed to deleteLater() where the layout may still contain items
        widget.setParent(None)
        # Delete from dictionary:
        del self.controllerWidgetsDict[widget.address]

    def _setCustomTempAll(self):
        '''
        Handles behavior of the custom temperature line edit
        '''
        tempK = self.ui.leSetCustomTemp.text()
        try:
            tempK = int(tempK)
        except Exception as e:
            print(e)
            self.statusEmitted.emit('Temperature must be an integer.')
        else:
            self._handleSetTempAll(tempK)
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

    def _handleSetTempAll(self, tempK):
        '''
        Creates a worker to run the _setTempAll fn on a seperate thread.
        Running on a seperate thread is probably not as necessary as _readTempAll
        since it's run once per setpoint change
        '''
        tempC = self._k_to_c(tempK)
        worker = Worker(self._setTempAll, tempC)
        self.threadpool.start(worker)

    def _readTempAll(self):
        '''
        Reads current temp and setpoint for all controllers
        '''
        for address, controllerWidget in self.controllerWidgetsDict.items():
            controllerWidget.read('currentTemp')
        for address, controllerWidget in self.controllerWidgetsDict.items():
            controllerWidget.read('setpoint')

    def _handleTimerRead(self):
        '''
        Creates a worker to run the _readTempAll fn on a seperate thread
        '''
        worker = Worker(self._readTempAll)
        self.threadpool.start(worker)

    def _toggleTimerRead(self):
        '''
        Initiates the QTimer for the read queries (_handleTimerRead/_readTempAll)
        '''
        if not self.readTimer.isActive():
            self.readTimer.start(30000)
            self._handleTimerRead()
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
            self.statusEmitted.emit('Disconnected from {0}'.format(self.serial.port))

    def parseConfigFile(self, fileName):
        '''
        Handler for config file name emitted from config_tab widget
        '''
        config = configparser.ConfigParser()
        config.read(fileName)
        serialSettings = config['SERIAL']

        # Extract Serial Info:
        try:
            self.port = config['SERIAL']['port']
            self.baudrate = config['SERIAL']['baudrate']
            self.timeout = config['SERIAL']['timeout']

            for i, availablePort in enumerate(self.availablePorts):
                if self.port in availablePort:
                    #print(availablePort, i)
                    self.ui.cbSerial.setCurrentIndex(i)
        except Exception as e:
            print(e)
        else:
            print(self.port, self.baudrate, self.timeout)

        # Deal with Controller Info:
        try:
            controllers = [controller for controller in config.sections() if controller != 'SERIAL']
            if controllers == []:
                raise Exception('No controllers found in config file.')
        except Exception as e:
            print(e)
        else:
            self.controllerWidgetsDict = {int(config[controller]['address']): ControllerWidget(self.serial, controller.title(), int(config[controller]['address']), config[controller]['mode']) for controller in controllers}
            self._clearLayout()
            for address, controllerWidget in self.controllerWidgetsDict.items():
                self.scrollWidgetLayout.addWidget(controllerWidget)
                controllerWidget.widgetEmitted.connect(self._deleteWidget)
        return

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
