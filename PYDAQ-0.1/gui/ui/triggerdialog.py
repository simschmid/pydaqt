# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'triggerdialog.ui'
#
# Created: Thu Nov  3 20:33:09 2016
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

class Ui_TriggerDialog(object):
    def setupUi(self, TriggerDialog):
        TriggerDialog.setObjectName(_fromUtf8("TriggerDialog"))
        TriggerDialog.setEnabled(True)
        TriggerDialog.resize(261, 194)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(TriggerDialog.sizePolicy().hasHeightForWidth())
        TriggerDialog.setSizePolicy(sizePolicy)
        TriggerDialog.setMinimumSize(QtCore.QSize(261, 161))
        TriggerDialog.setMaximumSize(QtCore.QSize(261, 300))
        TriggerDialog.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.ok = QtGui.QPushButton(TriggerDialog)
        self.ok.setGeometry(QtCore.QRect(170, 160, 85, 27))
        self.ok.setObjectName(_fromUtf8("ok"))
        self.frame_2 = QtGui.QFrame(TriggerDialog)
        self.frame_2.setGeometry(QtCore.QRect(0, 10, 261, 151))
        self.frame_2.setFrameShape(QtGui.QFrame.NoFrame)
        self.frame_2.setFrameShadow(QtGui.QFrame.Plain)
        self.frame_2.setLineWidth(0)
        self.frame_2.setObjectName(_fromUtf8("frame_2"))
        self.formLayout = QtGui.QFormLayout(self.frame_2)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(self.frame_2)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.lineselector = QtGui.QComboBox(self.frame_2)
        self.lineselector.setAutoFillBackground(False)
        self.lineselector.setEditable(False)
        self.lineselector.setFrame(True)
        self.lineselector.setObjectName(_fromUtf8("lineselector"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.lineselector)
        self.label_2 = QtGui.QLabel(self.frame_2)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.triggervalue = QtGui.QDoubleSpinBox(self.frame_2)
        self.triggervalue.setMinimum(-1000.0)
        self.triggervalue.setMaximum(1000.0)
        self.triggervalue.setSingleStep(1.0)
        self.triggervalue.setObjectName(_fromUtf8("triggervalue"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.triggervalue)
        self.label_3 = QtGui.QLabel(self.frame_2)
        self.label_3.setMinimumSize(QtCore.QSize(0, 35))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout.setWidget(3, QtGui.QFormLayout.LabelRole, self.label_3)
        self.frajjje = QtGui.QFrame(self.frame_2)
        self.frajjje.setEnabled(True)
        self.frajjje.setMinimumSize(QtCore.QSize(0, 35))
        self.frajjje.setMaximumSize(QtCore.QSize(16777215, 30))
        self.frajjje.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frajjje.setFrameShadow(QtGui.QFrame.Raised)
        self.frajjje.setObjectName(_fromUtf8("frajjje"))
        self.gridLayout_2 = QtGui.QGridLayout(self.frajjje)
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.radioFalling = QtGui.QRadioButton(self.frajjje)
        self.radioFalling.setChecked(False)
        self.radioFalling.setObjectName(_fromUtf8("radioFalling"))
        self.gridLayout_2.addWidget(self.radioFalling, 0, 1, 1, 1)
        self.radioRising = QtGui.QRadioButton(self.frajjje)
        self.radioRising.setChecked(True)
        self.radioRising.setObjectName(_fromUtf8("radioRising"))
        self.gridLayout_2.addWidget(self.radioRising, 0, 2, 1, 1)
        self.formLayout.setWidget(3, QtGui.QFormLayout.FieldRole, self.frajjje)
        self.treshold = QtGui.QSpinBox(self.frame_2)
        self.treshold.setMinimum(2)
        self.treshold.setProperty("value", 3)
        self.treshold.setObjectName(_fromUtf8("treshold"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.treshold)
        self.label_4 = QtGui.QLabel(self.frame_2)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_4)

        self.retranslateUi(TriggerDialog)
        QtCore.QMetaObject.connectSlotsByName(TriggerDialog)

    def retranslateUi(self, TriggerDialog):
        TriggerDialog.setWindowTitle(_translate("TriggerDialog", "Trigger", None))
        self.ok.setText(_translate("TriggerDialog", "Ok", None))
        self.label.setText(_translate("TriggerDialog", "Line", None))
        self.label_2.setText(_translate("TriggerDialog", " Value", None))
        self.label_3.setText(_translate("TriggerDialog", "Triggerside", None))
        self.radioFalling.setText(_translate("TriggerDialog", "Falling", None))
        self.radioRising.setText(_translate("TriggerDialog", "Rising", None))
        self.label_4.setText(_translate("TriggerDialog", "Treshold", None))

