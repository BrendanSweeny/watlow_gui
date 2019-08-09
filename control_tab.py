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
        self.readTimer.timeout.connect(self.handleTimerRead)

        # Timer that handles blinking LED
        self.ledTimer = QTimer(self)
        self.ledTimer.timeout.connect(self.handleBlinkLED)

        # Threadpool to handle concurrent tasks (periodic controller reads):
        self.threadpool = QThreadPool()

        # Sets up the scroll widget to have vertical box layout for controllers:
        self.scrollWidget = QWidget()
        self.scrollWidgetLayout = QVBoxLayout()
        self.scrollWidgetLayout.setAlignment(Qt.AlignTop)
        self.scrollWidget.setLayout(self.scrollWidgetLayout)
        self.ui.scrollArea.setWidget(self.scrollWidget)

        # Available serial ports and descriptions
        self.availablePorts = self.populateSerialPorts()

        # Signals and Slots:
        self.ui.btnSerialConnect.clicked.connect(self.toggleConnect)
        self.ui.btnRefreshPorts.clicked.connect(self.populateSerialPorts)
        self.ui.btnSetCustomTemp.clicked.connect(self.setCustomTempAll)

        # Temperature set buttons:
        self.ui.btn100K.clicked.connect(lambda: self.handleSetTempAll(100))
        self.ui.btn200K.clicked.connect(lambda: self.handleSetTempAll(200))
        self.ui.btn400K.clicked.connect(lambda: self.handleSetTempAll(400))
        self.ui.btn500K.clicked.connect(lambda: self.handleSetTempAll(500))
        self.ui.btn600K.clicked.connect(lambda: self.handleSetTempAll(600))
        self.ui.btn700K.clicked.connect(lambda: self.handleSetTempAll(700))

    def handleManualAdd(self, controllerInfo):
        print(controllerInfo)
        name = controllerInfo[0]
        address = controllerInfo[1]
        mode = controllerInfo[2]
        controllerWidget = ControllerWidget(self.serial, name, address, mode)
        #self.deleteWidget(self.controllerWidgetsDict[address])
        self.controllerWidgetsDict[address] = controllerWidget
        self.scrollWidgetLayout.addWidget(controllerWidget)
        controllerWidget.widgetEmitted.connect(self.deleteWidget)

    def clearLayout(self):
        for i in reversed(range(self.scrollWidgetLayout.count())):
            self.scrollWidgetLayout.itemAt(i).widget().setParent(None)

    def deleteWidget(self, widget):
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

    def setCustomTempAll(self):
        '''
        Handles behavior of the custom temperature line edit
        '''
        temp = self.ui.leSetCustomTemp.text()
        try:
            temp = int(tempK)
        except Exception as e:
            print(e)
            self.statusEmitted.emit('Temperature must be an integer.')
        else:
            self.handleSetTempAll(tempK)

    def _k_to_c(self, k):
        return k - 273.15

    def handleSetTempAll(self, tempK):
        '''
        Creates a worker to run the setTempAll fn on a seperate thread.
        This is probably not as necessary as readTempAll
        '''
        tempC = self._k_to_c(tempK)
        worker = Worker(self.setTempAll, tempC)
        self.threadpool.start(worker)

    def handleTimerRead(self):
        '''
        Creates a worker to run the readTempAll fn on a seperate thread
        '''
        worker = Worker(self.readTempAll)
        self.threadpool.start(worker)

    def setTempAll(self, temp):
        '''
        Sets temperature of connected watlow controllers based on
        specified heat/cool mode
        '''
        for address, controllerWidget in self.controllerWidgetsDict.items():
            if controllerWidget.mode == 'heat' and temp > 25:
                controllerWidget.write('setpoint', temp)
            elif controllerWidget.mode == 'cool' and temp < 25:
                controllerWidget.write('setpoint', temp)

    def toggleBlinkLED(self):
        '''
        Starts/Stops blinking LED used to indicate that serial is open and
        periodic read QTimer is running
        '''
        if not self.ledTimer.isActive():
            self.ledTimer.start(1000)
            self.handleBlinkLED()
        elif self.ledTimer.isActive():
            self.ledTimer.stop()

    def handleBlinkLED(self):
        if self.ui.monitorLED.state:
            self.ui.monitorLED.changeState(False)
        else:
            self.ui.monitorLED.changeState(True)

    def toggleTimerRead(self):
        if not self.readTimer.isActive():
            self.readTimer.start(30000)
            self.handleTimerRead()
        elif self.readTimer.isActive():
            self.readTimer.stop()

    def readTempAll(self):
        '''
        Reads current temp and setpoint for all controllers
        '''
        for address, controllerWidget in self.controllerWidgetsDict.items():
            controllerWidget.read('currentTemp')
        for address, controllerWidget in self.controllerWidgetsDict.items():
            controllerWidget.read('setpoint')

    def populateSerialPorts(self):
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
            line = name + ', ' + description

            self.ui.cbSerial.addItem(line)
            outputList.append(name)
        return outputList

    def toggleConnect(self):
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
            self.serial.port = self.availablePorts[index]
            self.serial.baudrate = 38400 # Watlow controller default baudrate
            self.serial.timeout = 0.5
            self.serial.open()
            if self.controllerWidgetsDict:
                for address, controllerWidget in self.controllerWidgetsDict.items():
                    controllerWidget.updateSerial(self.serial)
            self.ui.btnSerialConnect.setText('Disconnect')
            self.ui.connectLED.changeState(True)
            self.statusEmitted.emit('Connected to {0}'.format(self.serial.port))
            self.toggleTimerRead()
            self.toggleBlinkLED()
        else:
            self.toggleTimerRead()
            self.toggleBlinkLED()
            self.ui.monitorLED.changeState(False)
            self.serial.flush()
            self.serial.close()
            self.ui.btnSerialConnect.setText('Connect')
            self.ui.connectLED.changeState(False)
            self.statusEmitted.emit('Disconnected from {0}'.format(self.serial.port))

    def handleFNameEmitted(self, fileName):
        '''
        Handler for config file name emitted from config_tab widget
        '''
        self.parseConfigFile(fileName)

    def parseConfigFile(self, fileName):
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
            self.clearLayout()
            for address, controllerWidget in self.controllerWidgetsDict.items():
                self.scrollWidgetLayout.addWidget(controllerWidget)
                controllerWidget.widgetEmitted.connect(self.deleteWidget)
        return

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ControlTabWidget()
    window.show()
    sys.exit(app.exec_())
