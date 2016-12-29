# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pydaq.ui'
#
# Created: Fri Oct 28 23:09:32 2016
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

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(720, 502)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.textBrowser = QtGui.QTextBrowser(self.centralwidget)
        self.textBrowser.setMaximumSize(QtCore.QSize(158, 16777215))
        self.textBrowser.setObjectName(_fromUtf8("textBrowser"))
        self.gridLayout.addWidget(self.textBrowser, 1, 0, 1, 1)
        self.graphicsView = QtGui.QGraphicsView(self.centralwidget)
        self.graphicsView.setObjectName(_fromUtf8("graphicsView"))
        self.gridLayout.addWidget(self.graphicsView, 1, 1, 1, 1)
        self.frame = QtGui.QFrame(self.centralwidget)
        self.frame.setMinimumSize(QtCore.QSize(0, 30))
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.frame)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setContentsMargins(-1, 0, -1, 0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.commandLinkButton = QtGui.QCommandLinkButton(self.frame)
        self.commandLinkButton.setMaximumSize(QtCore.QSize(80, 16777215))
        self.commandLinkButton.setObjectName(_fromUtf8("commandLinkButton"))
        self.horizontalLayout.addWidget(self.commandLinkButton)
        self.commandLinkButton_2 = QtGui.QCommandLinkButton(self.frame)
        self.commandLinkButton_2.setMaximumSize(QtCore.QSize(80, 16777215))
        self.commandLinkButton_2.setObjectName(_fromUtf8("commandLinkButton_2"))
        self.horizontalLayout.addWidget(self.commandLinkButton_2)
        self.commandLinkButton_3 = QtGui.QCommandLinkButton(self.frame)
        self.commandLinkButton_3.setMaximumSize(QtCore.QSize(80, 16777215))
        self.commandLinkButton_3.setObjectName(_fromUtf8("commandLinkButton_3"))
        self.horizontalLayout.addWidget(self.commandLinkButton_3)
        self.gridLayout.addWidget(self.frame, 0, 0, 1, 2, QtCore.Qt.AlignLeft)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.textBrowser.setHtml(_translate("MainWindow", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'Noto Sans\'; font-size:9pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">test</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>", None))
        self.commandLinkButton.setText(_translate("MainWindow", "Start", None))
        self.commandLinkButton_2.setText(_translate("MainWindow", "Record", None))
        self.commandLinkButton_3.setText(_translate("MainWindow", "Setting", None))

