# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'config_tab.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(470, 213)
        self.label_15 = QtWidgets.QLabel(Form)
        self.label_15.setGeometry(QtCore.QRect(30, 180, 121, 16))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_15.setFont(font)
        self.label_15.setObjectName("label_15")
        self.label_16 = QtWidgets.QLabel(Form)
        self.label_16.setGeometry(QtCore.QRect(250, 157, 121, 16))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_16.setFont(font)
        self.label_16.setObjectName("label_16")
        self.line_2 = QtWidgets.QFrame(Form)
        self.line_2.setGeometry(QtCore.QRect(20, 110, 421, 16))
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.leAddress = QtWidgets.QLineEdit(Form)
        self.leAddress.setGeometry(QtCore.QRect(250, 180, 61, 20))
        self.leAddress.setObjectName("leAddress")
        self.cbMode = QtWidgets.QComboBox(Form)
        self.cbMode.setGeometry(QtCore.QRect(330, 178, 69, 22))
        self.cbMode.setObjectName("cbMode")
        self.label_17 = QtWidgets.QLabel(Form)
        self.label_17.setGeometry(QtCore.QRect(330, 157, 121, 16))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_17.setFont(font)
        self.label_17.setObjectName("label_17")
        self.label_12 = QtWidgets.QLabel(Form)
        self.label_12.setGeometry(QtCore.QRect(20, 10, 231, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_12.setFont(font)
        self.label_12.setObjectName("label_12")
        self.label_13 = QtWidgets.QLabel(Form)
        self.label_13.setGeometry(QtCore.QRect(20, 120, 211, 31))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.label_13.setFont(font)
        self.label_13.setObjectName("label_13")
        self.btnOpenConfig = QtWidgets.QPushButton(Form)
        self.btnOpenConfig.setGeometry(QtCore.QRect(30, 60, 111, 23))
        self.btnOpenConfig.setObjectName("btnOpenConfig")
        self.btnAdd = QtWidgets.QPushButton(Form)
        self.btnAdd.setGeometry(QtCore.QRect(410, 178, 31, 23))
        self.btnAdd.setObjectName("btnAdd")
        self.label_18 = QtWidgets.QLabel(Form)
        self.label_18.setGeometry(QtCore.QRect(160, 157, 121, 16))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.label_18.setFont(font)
        self.label_18.setObjectName("label_18")
        self.leName = QtWidgets.QLineEdit(Form)
        self.leName.setGeometry(QtCore.QRect(160, 180, 71, 20))
        self.leName.setObjectName("leName")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.label_15.setText(_translate("Form", "Add Controller:"))
        self.label_16.setText(_translate("Form", "Address"))
        self.label_17.setText(_translate("Form", "Mode"))
        self.label_12.setText(_translate("Form", "Configure Using File (.ini):"))
        self.label_13.setText(_translate("Form", "Configure Manually:"))
        self.btnOpenConfig.setText(_translate("Form", "Open Config File"))
        self.btnAdd.setText(_translate("Form", "+"))
        self.label_18.setText(_translate("Form", "Name"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Form = QtWidgets.QWidget()
    ui = Ui_Form()
    ui.setupUi(Form)
    Form.show()
    sys.exit(app.exec_())
