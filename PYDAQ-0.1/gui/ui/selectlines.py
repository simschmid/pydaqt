# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'selectlines.ui'
#
# Created: Sun Oct 30 19:53:08 2016
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

class Ui_SelectLines(object):
    def setupUi(self, SelectLines):
        SelectLines.setObjectName(_fromUtf8("SelectLines"))
        SelectLines.resize(202, 218)
        self.buttonBox = QtGui.QDialogButtonBox(SelectLines)
        self.buttonBox.setGeometry(QtCore.QRect(-150, 180, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.lineslist = QtGui.QListWidget(SelectLines)
        self.lineslist.setGeometry(QtCore.QRect(10, 10, 181, 161))
        self.lineslist.setAlternatingRowColors(True)
        self.lineslist.setSelectionMode(QtGui.QAbstractItemView.ExtendedSelection)
        self.lineslist.setSelectionBehavior(QtGui.QAbstractItemView.SelectItems)
        self.lineslist.setProperty("isWrapping", False)
        self.lineslist.setLayoutMode(QtGui.QListView.SinglePass)
        self.lineslist.setSpacing(0)
        self.lineslist.setSelectionRectVisible(True)
        self.lineslist.setObjectName(_fromUtf8("lineslist"))

        self.retranslateUi(SelectLines)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), SelectLines.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), SelectLines.reject)
        QtCore.QMetaObject.connectSlotsByName(SelectLines)

    def retranslateUi(self, SelectLines):
        SelectLines.setWindowTitle(_translate("SelectLines", "Select Lines", None))
        self.lineslist.setSortingEnabled(False)

