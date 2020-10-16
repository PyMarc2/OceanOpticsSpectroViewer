# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'filterViewUi.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_simulationView(object):
    def setupUi(self, simulationView):
        simulationView.setObjectName("simulationView")
        simulationView.resize(713, 741)
        simulationView.setStyleSheet("\n"
"QWidget{\n"
"color:#0B0B0B;\n"
"font: 11pt \"OpenSans-Light\";\n"
"}\n"
"")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(simulationView)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.fr_control = QtWidgets.QFrame(simulationView)
        self.fr_control.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.fr_control.setFrameShadow(QtWidgets.QFrame.Raised)
        self.fr_control.setObjectName("fr_control")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.fr_control)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.AcquisitionControl = QtWidgets.QGroupBox(self.fr_control)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.AcquisitionControl.sizePolicy().hasHeightForWidth())
        self.AcquisitionControl.setSizePolicy(sizePolicy)
        self.AcquisitionControl.setAutoFillBackground(False)
        self.AcquisitionControl.setStyleSheet("border-color: rgb(0, 0, 0);")
        self.AcquisitionControl.setObjectName("AcquisitionControl")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.AcquisitionControl)
        self.verticalLayout.setObjectName("verticalLayout")
        self.pb_liveView = QFlashButton(self.AcquisitionControl)
        self.pb_liveView.setStyleSheet("")
        self.pb_liveView.setObjectName("pb_liveView")
        self.verticalLayout.addWidget(self.pb_liveView)
        self.pb_normalize = QtWidgets.QPushButton(self.AcquisitionControl)
        self.pb_normalize.setStyleSheet("")
        self.pb_normalize.setObjectName("pb_normalize")
        self.verticalLayout.addWidget(self.pb_normalize)
        self.pb_analyse = QtWidgets.QPushButton(self.AcquisitionControl)
        self.pb_analyse.setObjectName("pb_analyse")
        self.verticalLayout.addWidget(self.pb_analyse)
        self.horizontalLayout_2.addWidget(self.AcquisitionControl)
        self.AcquisitionSettings = QtWidgets.QGroupBox(self.fr_control)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.AcquisitionSettings.sizePolicy().hasHeightForWidth())
        self.AcquisitionSettings.setSizePolicy(sizePolicy)
        self.AcquisitionSettings.setAutoFillBackground(False)
        self.AcquisitionSettings.setStyleSheet("border-color: rgb(0, 0, 0);")
        self.AcquisitionSettings.setObjectName("AcquisitionSettings")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.AcquisitionSettings)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.widget = QtWidgets.QWidget(self.AcquisitionSettings)
        self.widget.setObjectName("widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.la_acqTime = QtWidgets.QLabel(self.widget)
        self.la_acqTime.setObjectName("la_acqTime")
        self.horizontalLayout.addWidget(self.la_acqTime)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.le_acqTime = QtWidgets.QLineEdit(self.widget)
        self.le_acqTime.setObjectName("le_acqTime")
        self.horizontalLayout.addWidget(self.le_acqTime)
        self.verticalLayout_2.addWidget(self.widget)
        self.widget_2 = QtWidgets.QWidget(self.AcquisitionSettings)
        self.widget_2.setObjectName("widget_2")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.widget_2)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.la_acqTime_2 = QtWidgets.QLabel(self.widget_2)
        self.la_acqTime_2.setObjectName("la_acqTime_2")
        self.horizontalLayout_3.addWidget(self.la_acqTime_2)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.le_acqTime_2 = QtWidgets.QLineEdit(self.widget_2)
        self.le_acqTime_2.setObjectName("le_acqTime_2")
        self.horizontalLayout_3.addWidget(self.le_acqTime_2)
        self.verticalLayout_2.addWidget(self.widget_2)
        self.widget_3 = QtWidgets.QWidget(self.AcquisitionSettings)
        self.widget_3.setObjectName("widget_3")
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout(self.widget_3)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.la_acqTime_3 = QtWidgets.QLabel(self.widget_3)
        self.la_acqTime_3.setObjectName("la_acqTime_3")
        self.horizontalLayout_4.addWidget(self.la_acqTime_3)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_4.addItem(spacerItem2)
        self.le_acqTime_3 = QtWidgets.QLineEdit(self.widget_3)
        self.le_acqTime_3.setObjectName("le_acqTime_3")
        self.horizontalLayout_4.addWidget(self.le_acqTime_3)
        self.verticalLayout_2.addWidget(self.widget_3)
        self.horizontalLayout_2.addWidget(self.AcquisitionSettings)
        self.verticalLayout_3.addWidget(self.fr_control)
        self.pyqtgraphWidget = GraphicsLayoutWidget(simulationView)
        self.pyqtgraphWidget.setObjectName("pyqtgraphWidget")
        self.verticalLayout_3.addWidget(self.pyqtgraphWidget)

        self.retranslateUi(simulationView)
        QtCore.QMetaObject.connectSlotsByName(simulationView)

    def retranslateUi(self, simulationView):
        _translate = QtCore.QCoreApplication.translate
        simulationView.setWindowTitle(_translate("simulationView", "Form"))
        self.AcquisitionControl.setTitle(_translate("simulationView", "Acquisition Control"))
        self.pb_liveView.setText(_translate("simulationView", "Live View"))
        self.pb_normalize.setText(_translate("simulationView", "Normalize Reference"))
        self.pb_analyse.setText(_translate("simulationView", "Analyse Filter"))
        self.AcquisitionSettings.setTitle(_translate("simulationView", "Acquisition settings"))
        self.la_acqTime.setText(_translate("simulationView", "exposureTime"))
        self.le_acqTime.setText(_translate("simulationView", "100"))
        self.la_acqTime_2.setText(_translate("simulationView", "View IT"))
        self.le_acqTime_2.setText(_translate("simulationView", "100"))
        self.la_acqTime_3.setText(_translate("simulationView", "Acquisition IT"))
        self.le_acqTime_3.setText(_translate("simulationView", "100"))
from pyqtgraph import GraphicsLayoutWidget
from QFlashButton import QFlashButton
