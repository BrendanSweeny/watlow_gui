# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'controller.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(489, 84)
        self.labelName = QtWidgets.QLabel(Form)
        self.labelName.setGeometry(QtCore.QRect(10, 0, 341, 31))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.labelName.setFont(font)
        self.labelName.setObjectName("labelName")
        self.leSetTemp = QtWidgets.QLineEdit(Form)
        self.leSetTemp.setGeometry(QtCore.QRect(310, 50, 51, 20))
        self.leSetTemp.setObjectName("leSetTemp")
        self.lcdCurrentT = QtWidgets.QLCDNumber(Form)
        self.lcdCurrentT.setGeometry(QtCore.QRect(200, 30, 101, 41))
        self.lcdCurrentT.setObjectName("lcdCurrentT")
        self.btnSetTemp = QtWidgets.QPushButton(Form)
        self.btnSetTemp.setGeometry(QtCore.QRect(370, 48, 41, 23))
        self.btnSetTemp.setObjectName("btnSetTemp")
        self.lcdSetpoint = QtWidgets.QLCDNumber(Form)
        self.lcdSetpoint.setGeometry(QtCore.QRect(90, 30, 101, 41))
        self.lcdSetpoint.setObjectName("lcdSetpoint")
        self.cbMode = QtWidgets.QComboBox(Form)
        self.cbMode.setGeometry(QtCore.QRect(10, 48, 69, 22))
        self.cbMode.setObjectName("cbMode")
        self.line = QtWidgets.QFrame(Form)
        self.line.setGeometry(QtCore.QRect(10, 70, 471, 16))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.label_7 = QtWidgets.QLabel(Form)
        self.label_7.setGeometry(QtCore.QRect(360, 0, 51, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.label_7.setFont(font)
        self.label_7.setObjectName("label_7")
        self.labelAddress = QtWidgets.QLabel(Form)
        self.labelAddress.setGeometry(QtCore.QRect(420, 0, 51, 31))
        font = QtGui.QFont()
        font.setPointSize(10)
        self.labelAddress.setFont(font)
        self.labelAddress.setObjectName("labelAddress")
        self.connectLED = LEDWidget(Form)
        self.connectLED.setGeometry(QtCore.QRect(460, 10, 21, 21))
        self.connectLED.setObjectName("connectLED")
        self.btnDelete = QtWidgets.QPushButton(Form)
        self.btnDelete.setGeometry(QtCore.QRect(420, 48, 51, 23))
        self.btnDelete.setObjectName("btnDelete")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.labelName.setText(_translate("Form", "Name"))
        self.btnSetTemp.setText(_translate("Form", "Set"))
        self.label_7.setText(_translate("Form", "Address:"))
        self.labelAddress.setText(_translate("Form", "None"))
        self.btnDelete.setText(_translate("Form", "Delete"))
from led import LEDWidget


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
