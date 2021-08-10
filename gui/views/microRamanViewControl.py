from PyQt5.QtCore import pyqtSignal, Qt, QThreadPool, QThread, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QWidget, QFileDialog
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5 import uic

import pyqtgraph as pg
from PyQt5.Qt import QPixmap

from tkinter.filedialog import askopenfile
import pandas as pd
import numpy as np
import fnmatch
import ctypes
import time
import sys
import csv
import re
import os
# from hardwarelibrary.notificationcenter import NotificationCenter as notif

application_path = os.path.abspath("")


UiPath = os.path.dirname(os.path.realpath(__file__)) + '{0}microRamanViewUi.ui'.format(os.sep)
Ui_MainWindow, QtBaseClass = uic.loadUiType(UiPath)

class WindowControl(QWidget, Ui_MainWindow):
    def __init__(self, model=None):
        super(WindowControl, self).__init__()
        self.setupUi(self)
        self.model = model

        self.doSliderPositionAreInitialize = False
        self.deviceConnected = False
        self.visualWithoutBackground = True
        self.colorRangeViewEnable = True
        self.globalMaximum = True
        self.waveNumber = True
        self.folderPath = ""

        self.appControl = None
        self.lastError = None

        self.mousePositionX = 0
        self.mousePositionY = 0

        self.rangeLen = 1024
        self.minWave = 0

        self.connectWidgets()
        self.updateSliderStatus()
        self.initializeButtons()

        # notif().addObserver(self, self.acquisitionDone, "Map acquisition done or interrupted.")

    def createErrorDialogs(self, error):
        error = str(error)
        if self.lastError == error:
            pass
        else:
            self.lastError = error
            self.warningDialog = QMessageBox()
            self.warningDialog.setIcon(QMessageBox.Information)
            self.warningDialog.setText(f"{error}")
            self.warningDialog.setWindowTitle("Warning")
            self.warningDialog.setStandardButtons(QMessageBox.Ok)
            self.warningDialog.exec_()

    def connectWidgets(self):
        self.cb_substractBackground.stateChanged.connect(self.substractBackground)
        self.cb_colorRangeView.stateChanged.connect(self.colorRangeViewStatus)

        self.cmb_measureUnit.currentTextChanged.connect(self.setMeasureUnit)
        self.cmb_set_maximum.currentIndexChanged.connect(self.setMaximum)
        self.cmb_wave.currentIndexChanged.connect(self.setRangeToWave)

        self.dSlider_red.valueChanged.connect(self.setColorRange)
        self.dSlider_green.valueChanged.connect(self.setColorRange)
        self.dSlider_blue.valueChanged.connect(self.setColorRange)

        self.graph_rgb.scene().sigMouseMoved.connect(self.mouseMoved)

        self.pb_saveWithoutBackground.clicked.connect(self.saveWithoutBackground)
        self.pb_sweepAlternate.clicked.connect(self.sweepDirectionOther)
        self.pb_connectDetection.clicked.connect(self.connectDetection)
        self.pb_background.clicked.connect(self.acquireBackground)
        self.pb_sweepSame.clicked.connect(self.sweepDirectionSame)
        self.pb_connectLight.clicked.connect(self.connectLight)
        self.pb_connectStage.clicked.connect(self.connectStage)
        self.pb_launch.clicked.connect(self.launchAcquisition)
        self.pb_findDevices.clicked.connect(self.findDevices)
        self.pb_stop.clicked.connect(self.stopAcquisition)
        self.pb_saveImage.clicked.connect(self.saveImage)

        self.sb_highRed.valueChanged.connect(self.updateSliderStatus)
        self.sb_lowRed.valueChanged.connect(self.updateSliderStatus)
        self.sb_highGreen.valueChanged.connect(self.updateSliderStatus)
        self.sb_lowGreen.valueChanged.connect(self.updateSliderStatus)
        self.sb_highBlue.valueChanged.connect(self.updateSliderStatus)
        self.sb_lowBlue.valueChanged.connect(self.updateSliderStatus)
        self.sb_acqTime.valueChanged.connect(self.setIntegrationTime)
        self.sb_exposure.valueChanged.connect(self.setExposureTime)
        self.sb_height.textChanged.connect(self.setHeight)
        self.sb_width.textChanged.connect(self.setWidth)
        self.sb_step.textChanged.connect(self.setStep)

        self.le_fileName.editingFinished.connect(self.selectFileName)
        self.tb_folderPath.clicked.connect(self.selectSaveFolder)

    def enableAllButtons(self):
        self.cb_substractBackground.setEnabled(True)
        self.cmb_selectDetection.setEnabled(True)
        self.cmb_selectLight.setEnabled(True)
        self.cmb_selectStage.setEnabled(True)
        self.cmb_measureUnit.setEnabled(True)
        self.le_folderPath.setEnabled(True)
        self.le_laser.setEnabled(True)
        self.pb_findDevices.setEnabled(True)
        self.pb_saveWithoutBackground.setEnabled(True)
        self.pb_connectDetection.setEnabled(True)
        self.pb_sweepAlternate.setEnabled(True)
        self.pb_connectLight.setEnabled(True)
        self.pb_connectStage.setEnabled(True)
        self.pb_background.setEnabled(True)
        self.pb_sweepSame.setEnabled(True)
        self.sb_exposure.setEnabled(True)
        self.sb_acqTime.setEnabled(True)
        self.sb_height.setEnabled(True)
        self.sb_width.setEnabled(True)
        self.sb_step.setEnabled(True)
        self.tb_folderPath.setEnabled(True)
        self.le_fileName.setEnabled(True)

        self.cb_substractBackground.setStyleSheet("")
        self.cmb_selectDetection.setStyleSheet("")
        self.cmb_selectLight.setStyleSheet("")
        self.cmb_selectStage.setStyleSheet("")
        self.cmb_measureUnit.setStyleSheet("")
        self.le_folderPath.setStyleSheet("")
        self.le_laser.setStyleSheet("")
        self.pb_findDevices.setStyleSheet("")
        self.pb_saveWithoutBackground.setStyleSheet("")
        self.pb_connectDetection.setStyleSheet("")
        self.pb_sweepAlternate.setStyleSheet("")
        self.pb_connectLight.setStyleSheet("")
        self.pb_connectStage.setStyleSheet("")
        self.pb_background.setStyleSheet("")
        self.pb_sweepSame.setStyleSheet("")
        self.sb_exposure.setStyleSheet("")
        self.sb_acqTime.setStyleSheet("")
        self.sb_height.setStyleSheet("")
        self.sb_width.setStyleSheet("")
        self.sb_step.setStyleSheet("")
        self.tb_folderPath.setStyleSheet("")
        self.le_fileName.setStyleSheet("")

    def disableAllButtons(self):
        self.cb_substractBackground.setEnabled(False)
        self.cmb_selectDetection.setEnabled(False)
        self.cmb_selectLight.setEnabled(False)
        self.cmb_selectStage.setEnabled(False)
        self.cmb_measureUnit.setEnabled(False)
        self.le_folderPath.setEnabled(False)
        self.le_laser.setEnabled(False)
        self.pb_findDevices.setEnabled(False)
        self.pb_saveWithoutBackground.setEnabled(False)
        self.pb_connectDetection.setEnabled(False)
        self.pb_sweepAlternate.setEnabled(False)
        self.pb_connectLight.setEnabled(False)
        self.pb_connectStage.setEnabled(False)
        self.pb_background.setEnabled(False)
        self.pb_sweepSame.setEnabled(False)
        self.sb_exposure.setEnabled(False)
        self.sb_acqTime.setEnabled(False)
        self.sb_height.setEnabled(False)
        self.sb_width.setEnabled(False)
        self.sb_step.setEnabled(False)
        self.tb_folderPath.setEnabled(False)
        self.le_fileName.setEnabled(False)

        self.cb_substractBackground.setStyleSheet("background-color: rgb(40, 40, 40)")
        self.cmb_selectDetection.setStyleSheet("background-color: rgb(40, 40, 40)")
        self.cmb_selectLight.setStyleSheet("background-color: rgb(40, 40, 40)")
        self.cmb_selectStage.setStyleSheet("background-color: rgb(40, 40, 40)")
        self.cmb_measureUnit.setStyleSheet("background-color: rgb(40, 40, 40)")
        self.le_folderPath.setStyleSheet("background-color: rgb(40, 40, 40)")
        self.le_laser.setStyleSheet("background-color: rgb(40, 40, 40)")
        self.pb_findDevices.setStyleSheet("background-color: rgb(40, 40, 40)")
        self.pb_saveWithoutBackground.setStyleSheet("background-color: rgb(40, 40, 40)")
        self.pb_connectDetection.setStyleSheet("background-color: rgb(40, 40, 40)")
        self.pb_sweepAlternate.setStyleSheet("background-color: rgb(40, 40, 40)")
        self.pb_connectLight.setStyleSheet("background-color: rgb(40, 40, 40)")
        self.pb_connectStage.setStyleSheet("background-color: rgb(40, 40, 40)")
        self.pb_background.setStyleSheet("background-color: rgb(40, 40, 40)")
        self.pb_sweepSame.setStyleSheet("background-color: rgb(40, 40, 40)")
        self.sb_exposure.setStyleSheet("background-color: rgb(40, 40, 40)")
        self.sb_acqTime.setStyleSheet("background-color: rgb(40, 40, 40)")
        self.sb_height.setStyleSheet("background-color: rgb(40, 40, 40)")
        self.sb_width.setStyleSheet("background-color: rgb(40, 40, 40)")
        self.sb_step.setStyleSheet("background-color: rgb(40, 40, 40)")
        self.tb_folderPath.setStyleSheet("background-color: rgb(40, 40, 40)")
        self.le_fileName.setStyleSheet("background-color: rgb(40, 40, 40)")

    def initializeButtons(self):
        self.pb_sweepSame.setIcons(QPixmap("./gui/misc/icons/sweep_same.png").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
                                   QPixmap("./gui/misc/icons/sweep_same_hover.png").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
                                   QPixmap("./gui/misc/icons/sweep_same_clicked.png").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
                                   QPixmap("./gui/misc/icons/sweep_same_selected.png").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.pb_sweepSame.status = True
        self.pb_sweepSame.setEnabled(False)

        self.pb_sweepAlternate.setIcons(QPixmap("./gui/misc/icons/sweep_alternate.png").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
                                        QPixmap("./gui/misc/icons/sweep_alternate_hover.png").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
                                        QPixmap("./gui/misc/icons/sweep_alternate_clicked.png").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
                                        QPixmap("./gui/misc/icons/sweep_alternate_selected.png").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    # Device Connection
    def findDevices(self):
        self.lightDevices = ["halogenSpectrum", "randomSpectrum"]
        self.listStageDevices = self.appControl.listStageDevices()
        self.listSpecDevices = self.appControl.listSpecDevices()
        self.cmb_selectDetection.clear()
        self.cmb_selectDetection.addItems(self.listSpecDevices)
        self.cmb_selectLight.clear()
        self.cmb_selectLight.addItems(self.lightDevices)
        self.cmb_selectStage.clear()
        self.cmb_selectStage.addItems(self.listStageDevices)
        self.deviceConnected = True

        self.pb_connectLight.setEnabled(True)
        self.pb_connectLight.setStyleSheet("")
        self.pb_connectStage.setEnabled(True)
        self.pb_connectStage.setStyleSheet("")
        self.pb_connectDetection.setEnabled(True)
        self.pb_connectDetection.setStyleSheet("")
        self.cmb_selectDetection.setEnabled(True)
        self.cmb_selectDetection.setStyleSheet("")
        self.cmb_selectLight.setEnabled(True)
        self.cmb_selectLight.setStyleSheet("")
        self.cmb_selectStage.setEnabled(True)
        self.cmb_selectStage.setStyleSheet("")

    def connectDetection(self):
        if self.le_laser.text() == "":
            self.errorLaser()
        else:
            try:
                laser = int(self.le_laser.text())
                self.appControl.setLaserWavelength(laser)
                index = self.cmb_selectDetection.currentIndex()
                waves = self.appControl.connectDetection(index)
                self.appControl.setWavelength(waves)
                self.setRangeToWave()
                self.updateSliderStatus()
                self.cmb_wave.setEnabled(True)
                self.cmb_wave.setStyleSheet("")
                if index == 0:
                    self.cb_lightSource.setStyleSheet("QCheckBox::indicator{background-color: rgb(0, 255, 0);}")
                else:
                    self.cb_lightSource.setStyleSheet("QCheckBox::indicator{background-color: rgb(80, 80, 80);}")
                self.cb_detection.setStyleSheet("QCheckBox::indicator{background-color: rgb(0, 255, 0);}")
            except Exception as e:
                print(e)
                self.errorLaser()

    def connectLight(self):
        if self.cmb_selectDetection.currentIndex() == 0:
            index = self.cmb_selectLight.currentIndex()
            self.appControl.connectLight(index)
        else:
            pass

    def connectStage(self):
        index = self.cmb_selectStage.currentIndex()
        self.appControl.connectStage(index)
        self.cb_stage.setStyleSheet("QCheckBox::indicator{background-color: rgb(0, 255, 0);}")

    def errorDetection(self):
        self.pb_connectDetection.setStyleSheet("background-color: rgb(255, 0, 0)")
        QTimer.singleShot(50, lambda: self.pb_connectDetection.setStyleSheet(""))

    def errorLight(self):
        self.pb_connectLight.setStyleSheet("background-color: rgb(255, 0, 0)")
        QTimer.singleShot(50, lambda: self.pb_connectLight.setStyleSheet(""))

    def errorStage(self):
        self.pb_connectStage.setStyleSheet("background-color: rgb(255, 0, 0)")
        QTimer.singleShot(50, lambda: self.pb_connectStage.setStyleSheet(""))

    def errorFindDevice(self):
        self.pb_findDevices.setStyleSheet("background-color: rgb(255, 0, 0)")
        QTimer.singleShot(50, lambda: self.pb_findDevices.setStyleSheet(""))

    # Capture Controls
    def selectFileName(self):
        fileName = self.le_fileName.text()
        self.appControl.setFileName(fileName)

    def selectSaveFolder(self):
        self.folderPath = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if self.folderPath != "":
            self.le_folderPath.setText(self.folderPath)
        self.appControl.setFolderPath(self.folderPath)

    def errorFolderName(self):
        self.le_folderPath.setStyleSheet("background-color: rgb(255, 0, 0)")
        QTimer.singleShot(50, lambda: self.le_folderPath.setStyleSheet(""))

    def saveImage(self):
        matrixRGB = self.appControl.matrixRGB(self.globalMaximum, self.visualWithoutBackground)
        self.appControl.saveImage(matrixRGB)

    # Background Controls
    def substractBackground(self):
        backgroundData = self.appControl.backgroundData
        if backgroundData == []:
            self.errorBackground()
            if self.cb_substractBackground.checkState() == 2:
                QTimer.singleShot(1, lambda: self.cb_substractBackground.setCheckState(0))
        else:
            if self.cb_substractBackground.checkState() == 2:
                self.visualWithoutBackground = True
            if self.cb_substractBackground.checkState() == 0:
                self.visualWithoutBackground = False
            laser = self.appControl.getLaser()
            matrixRGB = self.appControl.matrixRGB(self.globalMaximum, self.visualWithoutBackground)
            waves = self.appControl.waves(laser)
            self.updateSpectrumPlot(waves)
            self.updateRGBPlot(matrixRGB)

    def saveWithoutBackground(self):
        self.disableAllButtons()
        self.appControl.saveWithoutBackground()
        self.enableAllButtons()

    def errorBackground(self):
        self.pb_background.setStyleSheet("background-color: rgb(255, 0, 0)")
        QTimer.singleShot(50, lambda: self.pb_background.setStyleSheet(""))

    # Info Laser
    def errorLaser(self):
        self.le_laser.setStyleSheet("background-color: rgb(255, 0, 0)")
        QTimer.singleShot(50, lambda: self.le_laser.setStyleSheet(""))

    # Acquisition Settings
    def setWidth(self):
        width = self.sb_width.value()
        self.appControl.setWidth(width)

    def setHeight(self):
        height = self.sb_height.value()
        self.appControl.setHeight(height)

    def setStep(self):
        step = self.sb_step.value()
        self.appControl.setStep(step)

    def setMeasureUnit(self):
        measureUnit = self.cmb_measureUnit.currentText()
        self.appControl.setMeasureUnit(measureUnit)

    def setExposureTime(self):
        exposureTime = self.sb_exposure.value()
        self.appControl.setExposureTime(exposureTime)

    def setIntegrationTime(self):
        acqTime = self.sb_acqTime.value()
        self.appControl.setIntegrationTime(acqTime)

    def sweepDirectionSame(self):
        if self.pb_sweepSame.status == True:
            self.pb_sweepAlternate.status = False
        else:
            self.pb_sweepAlternate.status = True
        self.pb_sweepAlternate.enterEvent("An Event")
        self.pb_sweepSame.setEnabled(False)
        self.pb_sweepAlternate.setEnabled(True)
        self.appControl.sweepDirectionSame()

    def sweepDirectionOther(self):
        if self.pb_sweepAlternate.status == True:
            self.pb_sweepSame.status = False
        else:
            self.pb_sweepSame.status = True
        self.pb_sweepSame.enterEvent("An Event")
        self.pb_sweepAlternate.setEnabled(False)
        self.pb_sweepSame.setEnabled(True)
        self.appControl.sweepDirectionOther()

    # Acquisition Control
    def acquireBackground(self):
        stageState = self.appControl.stageConnected()
        spectroState = self.appControl.spectroConnected()
        if self.folderPath == "":
            self.errorFolderName()
        elif self.le_laser.text() == "":
            self.errorLaser()
        elif not self.deviceConnected:
            self.errorFindDevice()
        elif not spectroState:
            self.errorDetection()
        elif not stageState:
            self.errorStage()
        else:
            self.disableAllButtons()
            self.appControl.acquireBackground()
            # self.appControl.backgroundLoop.join()
            self.enableAllButtons()

    def launchAcquisition(self):
        self.lastError = None
        try:
            stageState = self.appControl.stageConnected()
            spectroState = self.appControl.spectroConnected()
            if self.folderPath == "":
                    self.errorFolderName()
            elif self.le_laser.text() == "":
                self.errorLaser()
            elif not self.deviceConnected:
                self.errorFindDevice()
            elif not spectroState:
                self.errorDetection()
            elif not stageState:
                self.errorStage()
                
            else:
                self.appControl.deleteSpectra()
                self.pb_saveImage.setEnabled(True)
                self.pb_saveImage.setStyleSheet("")
                self.cmb_wave.setEnabled(False)
                self.cmb_wave.setStyleSheet("background-color: rgb(40, 40, 40)")
                self.createPlotSpectrum()
                self.createPlotRGB()
                self.disableAllButtons()
                self.appControl.launchAcquisition()
                # self.appControl.startRefreshRGBLoop()  # TODO when threads are ok
                # TODO see if with thread okay... probably will connect with signal?

        except Exception as e:
            self.createErrorDialogs(e)

    def stopAcquisition(self):
        self.cmb_wave.setEnabled(True)
        self.cmb_wave.setStyleSheet("")
        self.enableAllButtons()
        self.appControl.stopAcquisition()
        #self.appControl.quitLoopRGB = True # TODO when threads are ok or not because still updated afterwards...

    def acquisitionDone(self, *args):
        self.cmb_wave.setEnabled(True)
        self.cmb_wave.setStyleSheet("")
        self.enableAllButtons()

    # Image Controls
    def createPlotRGB(self):
        self.graph_rgb.clear()
        self.plotViewBox = self.graph_rgb.addViewBox()
        self.plotViewBox.enableAutoRange()
        self.plotViewBox.invertY(True)
        self.plotViewBox.setAspectLocked()

    def createPlotSpectrum(self):
        self.graph_spectre.clear()
        self.plotItem = self.graph_spectre.addPlot()
        self.plotSpectrum = self.plotItem.plot()
        self.plotRedRange = self.plotItem.plot()
        self.plotGreenRange = self.plotItem.plot()
        self.plotBlueRange = self.plotItem.plot()
        self.plotBlack = self.plotItem.plot()
        self.plotItem.enableAutoRange()

    def mouseMoved(self, pos):
        try:
            value = self.plotViewBox.mapSceneToView(pos)
            valueSTR = str(value)
            valueMin = valueSTR.find("(")
            valueMax = valueSTR.find(")")
            position = valueSTR[valueMin+1:valueMax]
            position = position.split(",")
            positionY = int(float(position[1]))
            positionX = int(float(position[0]))

            if positionX <= -1 or positionY <= -1:
                pass

            elif positionX >= self.sb_width.value():
                pass

            elif positionY >= self.sb_height.value():
                pass

            else:
                self.mousePositionX = positionX
                self.mousePositionY = positionY
                laser = self.appControl.getLaser()
                waves = self.appControl.waves(laser)
                self.updateSpectrumPlot(waves)
        except Exception as e:
            pass

    def setMaximum(self):
        if self.cmb_set_maximum.currentIndex() == 0:
            self.globalMaximum = True
        else:
            self.globalMaximum = False
        try:
            laser = self.appControl.getLaser()
            matrixRGB = self.appControl.matrixRGB(self.globalMaximum, self.visualWithoutBackground)
            waves = self.appControl.waves(laser)
            self.updateRGBPlot(matrixRGB)
        except:
            pass

    def setColorRange(self):
        colorValues = self.currentSliderValues()
        self.sb_lowRed.setValue(self.mappingOnSpinBox(colorValues[0]))
        self.sb_highRed.setValue(self.mappingOnSpinBox(colorValues[1]))
        self.sb_lowGreen.setValue(self.mappingOnSpinBox(colorValues[2]))
        self.sb_highGreen.setValue(self.mappingOnSpinBox(colorValues[3]))
        self.sb_lowBlue.setValue(self.mappingOnSpinBox(colorValues[4]))
        self.sb_highBlue.setValue(self.mappingOnSpinBox(colorValues[5]))

    def setRangeToWave(self):
        if self.cmb_wave.currentIndex() == 0: 
            self.waveNumber = True
        else:
            self.waveNumber = False 
        laser = self.appControl.getLaser()
        waves = self.appControl.waves(laser)

        self.minWave = round(min(waves))
        self.rangeLen = round(max(waves) - min(waves))
        self.maxWave = int(max(waves))

        colorValues = self.currentSliderValues()

        self.sb_highRed.setMaximum(self.maxWave)
        self.sb_lowRed.setMaximum(self.maxWave-1)
        self.sb_highGreen.setMaximum(self.maxWave)
        self.sb_lowGreen.setMaximum(self.maxWave-1)
        self.sb_highBlue.setMaximum(self.maxWave)
        self.sb_lowBlue.setMaximum(self.maxWave-1)

        self.sb_highRed.setMinimum(self.minWave)
        self.sb_lowRed.setMinimum(self.minWave)
        self.sb_highGreen.setMinimum(self.minWave)
        self.sb_lowGreen.setMinimum(self.minWave)
        self.sb_highBlue.setMinimum(self.minWave)
        self.sb_lowBlue.setMinimum(self.minWave)

        self.sb_lowRed.setValue(self.mappingOnSpinBox(colorValues[0]))
        self.sb_highRed.setValue(self.mappingOnSpinBox(colorValues[1]))
        self.sb_lowGreen.setValue(self.mappingOnSpinBox(colorValues[2]))
        self.sb_highGreen.setValue(self.mappingOnSpinBox(colorValues[3]))
        self.sb_lowBlue.setValue(self.mappingOnSpinBox(colorValues[4]))
        self.sb_highBlue.setValue(self.mappingOnSpinBox(colorValues[5]))

        self.updateSliderStatus()

    def mappingOnSlider(self, value):
        return round(((value - self.minWave)/self.rangeLen) * 1024)

    def mappingOnSpinBox(self, value):
        return round((value * self.rangeLen) + self.minWave)

    def currentSliderValues(self):
        lowRedValue = self.dSlider_red.get_left_thumb_value() / 1024
        highRedValue = self.dSlider_red.get_right_thumb_value() / 1024
        lowGreenValue = self.dSlider_green.get_left_thumb_value() / 1024
        highGreenValue = self.dSlider_green.get_right_thumb_value() / 1024
        lowBlueValue = self.dSlider_blue.get_left_thumb_value() / 1024
        highBlueValue = self.dSlider_blue.get_right_thumb_value() / 1024
        return [lowRedValue, highRedValue, lowGreenValue, highGreenValue, lowBlueValue, highBlueValue]

    def updateRGBPlot(self, matrixRGB):
        if matrixRGB is not None:
            matrixRGB = matrixRGB.transpose(1, 0, 2)
        vb = pg.ImageItem(image=matrixRGB)
        self.plotViewBox.addItem(vb)

    def updateSpectrumPlot(self, waves):
        spectrum = self.appControl.spectrum(self.mousePositionX, self.mousePositionY, self.visualWithoutBackground)
        try:
            maximum = max(spectrum)
            minimum = min(spectrum) - 1
        except Exception as e:
            maximum = 1
            minimum = 0

        wavesLen = len(waves)
        colorValues = self.currentSliderValues()

        if self.colorRangeViewEnable:
            lowRed = int( colorValues[0] * wavesLen )
            highRed = int( colorValues[1] * wavesLen - 1 )
            lowGreen = int( colorValues[2] * wavesLen )
            highGreen = int( colorValues[3] * wavesLen - 1 )
            lowBlue = int( colorValues[4] * wavesLen )
            highBlue = int( colorValues[5] * wavesLen - 1 )

            redRange = np.full(wavesLen, minimum)
            redRange[lowRed] = maximum
            redRange[highRed] = maximum

            greenRange = np.full(wavesLen, minimum)
            greenRange[lowGreen] = maximum
            greenRange[highGreen] = maximum

            blueRange = np.full(wavesLen, minimum)
            blueRange[lowBlue] = maximum
            blueRange[highBlue] = maximum

            self.plotRedRange.setData(waves, redRange, pen=(255, 0, 0))
            self.plotGreenRange.setData(waves, greenRange, pen=(0, 255, 0))
            self.plotBlueRange.setData(waves, blueRange, pen=(0, 0, 255))
            self.plotBlack.setData(waves, np.full(wavesLen, minimum), pen=(0, 0, 0))

        if not self.colorRangeViewEnable:
            self.plotRedRange.setData(waves, np.full(wavesLen, minimum), pen=(0, 0, 0))
            self.plotGreenRange.setData(waves, np.full(wavesLen, minimum), pen=(0, 0, 0))
            self.plotBlueRange.setData(waves, np.full(wavesLen, minimum), pen=(0, 0, 0))
            self.plotBlack.setData(waves, np.full(wavesLen, minimum), pen=(0, 0, 0))

        self.plotSpectrum.setData(waves, spectrum)

    def updateSliderStatus(self):
        self.dSlider_red.set_left_thumb_value(self.mappingOnSlider(self.sb_lowRed.value()))
        self.dSlider_red.set_right_thumb_value(self.mappingOnSlider(self.sb_highRed.value()))
        self.dSlider_green.set_left_thumb_value(self.mappingOnSlider(self.sb_lowGreen.value()))
        self.dSlider_green.set_right_thumb_value(self.mappingOnSlider(self.sb_highGreen.value()))
        self.dSlider_blue.set_left_thumb_value(self.mappingOnSlider(self.sb_lowBlue.value()))
        self.dSlider_blue.set_right_thumb_value(self.mappingOnSlider(self.sb_highBlue.value()))

        if self.doSliderPositionAreInitialize:
            try:
                laser = self.appControl.getLaser()
                matrixRGB = self.appControl.matrixRGB(self.globalMaximum, self.visualWithoutBackground)
                waves = self.appControl.waves(laser)
                self.updateSpectrumPlot(waves)
                self.updateRGBPlot(matrixRGB)

            except:
                pass
        else:
            self.doSliderPositionAreInitialize = True

    def colorRangeViewStatus(self):  # GUI
        if self.cb_colorRangeView.checkState() == 2:
            self.colorRangeViewEnable = True
        if self.cb_colorRangeView.checkState() == 0:
            self.colorRangeViewEnable = False
        try:
            laser = self.appControl.getLaser()
            waves = self.appControl.waves(laser)
            self.updateSpectrumPlot(waves)
        except Exception:
            pass