# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'simulationViewUi.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_simulationView(object):
    def setupUi(self, simulationView):
        simulationView.setObjectName("simulationView")
        simulationView.resize(745, 741)
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
        self.pb_liveView = QtWidgets.QPushButton(self.AcquisitionControl)
        self.pb_liveView.setStyleSheet("")
        self.pb_liveView.setObjectName("pb_liveView")
        self.verticalLayout.addWidget(self.pb_liveView)
        self.pb_backgroundAcq = QtWidgets.QPushButton(self.AcquisitionControl)
        self.pb_backgroundAcq.setStyleSheet("")
        self.pb_backgroundAcq.setObjectName("pb_backgroundAcq")
        self.verticalLayout.addWidget(self.pb_backgroundAcq)
        self.pb_filterAcq = QtWidgets.QPushButton(self.AcquisitionControl)
        self.pb_filterAcq.setObjectName("pb_filterAcq")
        self.verticalLayout.addWidget(self.pb_filterAcq)
        self.pb_compute = QtWidgets.QPushButton(self.AcquisitionControl)
        self.pb_compute.setObjectName("pb_compute")
        self.verticalLayout.addWidget(self.pb_compute)
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
        self.le_acqTime = QtWidgets.QLineEdit(self.widget)
        self.le_acqTime.setObjectName("le_acqTime")
        self.horizontalLayout.addWidget(self.le_acqTime)
        self.verticalLayout_2.addWidget(self.widget)
        self.pb_settings = QtWidgets.QPushButton(self.AcquisitionSettings)
        self.pb_settings.setObjectName("pb_settings")
        self.verticalLayout_2.addWidget(self.pb_settings)
        self.horizontalLayout_2.addWidget(self.AcquisitionSettings)
        self.verticalLayout_3.addWidget(self.fr_control)
        self.widget_2 = GraphicsLayoutWidget(simulationView)
        self.widget_2.setObjectName("widget_2")
        self.verticalLayout_3.addWidget(self.widget_2)

        self.retranslateUi(simulationView)
        QtCore.QMetaObject.connectSlotsByName(simulationView)

    def retranslateUi(self, simulationView):
        _translate = QtCore.QCoreApplication.translate
        simulationView.setWindowTitle(_translate("simulationView", "Form"))
        self.AcquisitionControl.setTitle(_translate("simulationView", "Acquisition Control"))
        self.pb_liveView.setText(_translate("simulationView", "Live View"))
        self.pb_backgroundAcq.setText(_translate("simulationView", "Background Acquisition"))
        self.pb_filterAcq.setText(_translate("simulationView", "Filter Acquisition"))
        self.pb_compute.setText(_translate("simulationView", "Computer, Compute"))
        self.AcquisitionSettings.setTitle(_translate("simulationView", "Acquisition settings"))
        self.la_acqTime.setText(_translate("simulationView", "Acq. time (ms)"))
        self.le_acqTime.setText(_translate("simulationView", "100"))
        self.pb_settings.setText(_translate("simulationView", "Computer, Send settings"))

from graphicslayoutwidget import GraphicsLayoutWidget
