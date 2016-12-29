# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pydaq.ui'
#
# Created: Wed Nov 23 00:20:58 2016
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
        MainWindow.resize(720, 526)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setAnimated(True)
        self.centralwidget = QtGui.QWidget(MainWindow)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.gridLayout = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.fig = QtGui.QGraphicsView(self.centralwidget)
        self.fig.setObjectName(_fromUtf8("fig"))
        self.gridLayout.addWidget(self.fig, 1, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QtGui.QToolBar(MainWindow)
        self.toolBar.setObjectName(_fromUtf8("toolBar"))
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.menuBar = QtGui.QMenuBar(MainWindow)
        self.menuBar.setGeometry(QtCore.QRect(0, 0, 720, 27))
        self.menuBar.setObjectName(_fromUtf8("menuBar"))
        self.menuFile = QtGui.QMenu(self.menuBar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        MainWindow.setMenuBar(self.menuBar)
        self.plotcontrols = QtGui.QToolBar(MainWindow)
        self.plotcontrols.setObjectName(_fromUtf8("plotcontrols"))
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.plotcontrols)
        self.textdock0 = QtGui.QDockWidget(MainWindow)
        self.textdock0.setMinimumSize(QtCore.QSize(96, 121))
        self.textdock0.setMaximumSize(QtCore.QSize(9999, 524287))
        self.textdock0.setBaseSize(QtCore.QSize(100, 0))
        self.textdock0.setObjectName(_fromUtf8("textdock0"))
        self.dockWidgetContents_2 = QtGui.QWidget()
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.dockWidgetContents_2.sizePolicy().hasHeightForWidth())
        self.dockWidgetContents_2.setSizePolicy(sizePolicy)
        self.dockWidgetContents_2.setBaseSize(QtCore.QSize(100, 0))
        self.dockWidgetContents_2.setObjectName(_fromUtf8("dockWidgetContents_2"))
        self.verticalLayout = QtGui.QVBoxLayout(self.dockWidgetContents_2)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.text = QtGui.QPlainTextEdit(self.dockWidgetContents_2)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.text.sizePolicy().hasHeightForWidth())
        self.text.setSizePolicy(sizePolicy)
        self.text.setMinimumSize(QtCore.QSize(0, 0))
        self.text.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.text.setBaseSize(QtCore.QSize(100, 0))
        self.text.setMidLineWidth(1)
        self.text.setReadOnly(True)
        self.text.setTabStopWidth(1)
        self.text.setObjectName(_fromUtf8("text"))
        self.verticalLayout.addWidget(self.text)
        self.textdock0.setWidget(self.dockWidgetContents_2)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(1), self.textdock0)
        self.toolBar.addSeparator()
        self.menuBar.addAction(self.menuFile.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar", None))
        self.menuFile.setTitle(_translate("MainWindow", "File", None))
        self.plotcontrols.setWindowTitle(_translate("MainWindow", "toolBar_2", None))
        self.textdock0.setWindowTitle(_translate("MainWindow", "Terminal", None))

