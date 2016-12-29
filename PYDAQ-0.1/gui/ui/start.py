# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'start.ui'
#
# Created: Sun Oct 30 13:42:26 2016
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_StartDialog(object):
    def setupUi(self, StartDialog):
        StartDialog.setObjectName(_fromUtf8("StartDialog"))
        StartDialog.resize(401, 348)
        self.buttonBox = QtGui.QDialogButtonBox(StartDialog)
        self.buttonBox.setGeometry(QtCore.QRect(50, 310, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.frame = QtGui.QFrame(StartDialog)
        self.frame.setEnabled(True)
        self.frame.setGeometry(QtCore.QRect(10, 10, 381, 61))
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.formLayout = QtGui.QFormLayout(self.frame)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(self.frame)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.devices_cbox = QtGui.QComboBox(self.frame)
        self.devices_cbox.setObjectName(_fromUtf8("devices_cbox"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.devices_cbox)
        self.selected_dev_name = QtGui.QLabel(StartDialog)
        self.selected_dev_name.setGeometry(QtCore.QRect(20, 80, 361, 17))
        self.selected_dev_name.setObjectName(_fromUtf8("selected_dev_name"))
        self.dev_frame = QtGui.QScrollArea(StartDialog)
        self.dev_frame.setGeometry(QtCore.QRect(9, 99, 381, 212))
        self.dev_frame.setWidgetResizable(True)
        self.dev_frame.setObjectName(_fromUtf8("dev_frame"))
        self.scrollAreaWidgetContents = QtGui.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 379, 210))
        self.scrollAreaWidgetContents.setObjectName(_fromUtf8("scrollAreaWidgetContents"))
        self.dev_frame_layout = QtGui.QVBoxLayout(self.scrollAreaWidgetContents)
        self.dev_frame_layout.setObjectName(_fromUtf8("dev_frame_layout"))
        self.textBrowser = QtGui.QTextBrowser(self.scrollAreaWidgetContents)
        self.textBrowser.setObjectName(_fromUtf8("textBrowser"))
        self.dev_frame_layout.addWidget(self.textBrowser)
        self.dev_frame.setWidget(self.scrollAreaWidgetContents)

        self.retranslateUi(StartDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), StartDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), StartDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(StartDialog)

    def retranslateUi(self, StartDialog):
        StartDialog.setWindowTitle(_translate("StartDialog", "Dialog", None))
        self.label.setText(_translate("StartDialog", "Select Device", None))
        self.selected_dev_name.setText(_translate("StartDialog", "No Device Selected", None))
        self.textBrowser.setHtml(_translate("StartDialog", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Noto Sans\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Select a device to continue</p></body></html>", None))

