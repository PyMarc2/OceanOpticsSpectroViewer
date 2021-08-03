from PyQt5.QtCore import pyqtSignal, Qt, QThreadPool, QThread, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5 import uic

import pyqtgraph as pg

from tkinter.filedialog import askopenfile
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import fnmatch
import ctypes
import time
import sys
import csv
import re
import os

application_path = os.path.abspath("")

if sys.platform == "win32":
    myappid = u"mycompany.myproduct.subproduct.version" # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
else:
    pass

UiPath = os.path.dirname(os.path.realpath(__file__)) + '{0}WindowUI.ui'.format(os.sep)
Ui_MainWindow, QtBaseClass = uic.loadUiType(UiPath)

class WindowControl(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        self.setWindowIcon(QIcon(application_path + "{0}gui{0}misc{0}logo{0}logo.ico".format(os.sep)))
        self.appController = None

        self.doSliderPositionAreInitialize = False
        self.colorRangeViewEnable = True
        self.globalMaximum = True
        self.folderpath = ""
        self.waveNumber = True

        self.mousePositionX = 0
        self.mousePositionY = 0

        self.rangeLen = 1024
        self.minWave = 0

        self.connectWidgets()
        self.updateSliderStatus()

    def connectWidgets(self):
        self.cmb_wave.currentIndexChanged.connect(self.setRangeToWave)
        self.cmb_set_maximum.currentIndexChanged.connect(self.setMaximum)

        self.graph_rgb.scene().sigMouseMoved.connect(self.mouseMoved)

        self.dSlider_red.valueChanged.connect(self.setColorRange)
        self.dSlider_green.valueChanged.connect(self.setColorRange)
        self.dSlider_blue.valueChanged.connect(self.setColorRange)

        self.sb_highRed.valueChanged.connect(self.updateSliderStatus)
        self.sb_lowRed.valueChanged.connect(self.updateSliderStatus)
        self.sb_highGreen.valueChanged.connect(self.updateSliderStatus)
        self.sb_lowGreen.valueChanged.connect(self.updateSliderStatus)
        self.sb_highBlue.valueChanged.connect(self.updateSliderStatus)
        self.sb_lowBlue.valueChanged.connect(self.updateSliderStatus)

        self.cb_colorRangeView.stateChanged.connect(self.colorRangeViewStatus)

        self.pb_launch.clicked.connect(self.launchAcquisition)
        self.pb_stop.clicked.connect(self.stopAcquisition)
        self.pb_background.clicked.connect(self.acquireBackground)

        self.pb_sweepSame.clicked.connect(self.sweepDirectionSame)
        self.pb_sweepAlternate.clicked.connect(self.sweepDirectionOther)

        self.sb_acqTime.valueChanged.connect(self.setAcquisitionTime)
        self.sb_exposure.valueChanged.connect(self.setExposureTime)
        self.sb_step.textChanged.connect(self.setStep)

        self.sb_height.textChanged.connect(lambda: setattr(self, 'height', self.sb_height.value()))
        self.sb_width.textChanged.connect(lambda: setattr(self, 'width', self.sb_width.value()))

        def setHeight(self):
            height = self.sb_height.value()
            pass # Call fonction Justine

        def setWidth(self):
            width = self.sb_width.value()
            pass # call fonction Justine











        self.cb_delete_background.stateChanged.connect(self.update_without_background)

        self.cmb_measureUnit.currentTextChanged.connect(self.setMeasureUnit)

        self.pb_saveData.clicked.connect(self.save_matrixRGB)
        self.pb_connectLight.clicked.connect(self.connect_light)
        self.pb_connectStage.clicked.connect(self.connect_stage)
        self.pb_connectDetection.clicked.connect(self.connect_detection)
        self.pb_saveImage.clicked.connect(self.save_image)
        self.pb_save_without_background.clicked.connect(self.save_matrix_data_without_background)


        self.tb_folderPath.clicked.connect(self.select_save_folder)

    def enableAllButtons(self):
        self.cb_delete_background.setEnabled(True)
        self.cmb_selectDetection.setEnabled(True)
        self.cmb_selectLight.setEnabled(True)
        self.cmb_selectStage.setEnabled(True)
        self.cmb_magnitude.setEnabled(True)
        self.pb_save_without_background.setEnabled(True)
        self.pb_connectDetection.setEnabled(True)
        self.pb_sweepAlternate.setEnabled(True)
        self.pb_connectLight.setEnabled(True)
        self.pb_connectStage.setEnabled(True)
        self.pb_sweepSame.setEnabled(True)
        self.pb_background.setEnabled(True)
        self.sb_exposure.setEnabled(True)
        self.sb_acqTime.setEnabled(True)
        self.sb_height.setEnabled(True)
        self.sb_width.setEnabled(True)
        self.sb_step.setEnabled(True)
        self.tb_folderPath.setEnabled(True)
        self.le_fileName.setEnabled(True)

    def disableAllButtons(self):
        self.cb_delete_background.setEnabled(False)
        self.cmb_selectDetection.setEnabled(False)
        self.cmb_selectLight.setEnabled(False)
        self.cmb_selectStage.setEnabled(False)
        self.cmb_magnitude.setEnabled(False)
        self.pb_save_without_background.setEnabled(False)
        self.pb_connectDetection.setEnabled(False)
        self.pb_sweepAlternate.setEnabled(False)
        self.pb_connectLight.setEnabled(False)
        self.pb_connectStage.setEnabled(False)
        self.pb_sweepSame.setEnabled(False)
        self.pb_background.setEnabled(False)
        self.sb_exposure.setEnabled(False)
        self.sb_acqTime.setEnabled(False)
        self.sb_height.setEnabled(False)
        self.sb_width.setEnabled(False)
        self.sb_step.setEnabled(False)
        self.tb_folderPath.setEnabled(False)
        self.le_fileName.setEnabled(False)

    # Device Connection
    def selectSaveFolder(self):
        if self.le_laser.text() == "":
            self.errorLaser()
        else:
            try:
                laser = int(self.le_laser.text())
                self.folderPath = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
                self.appController.deleteSpectrum()
                self.appController.loadData(self.folderPath)
                matrixRGB = self.appController.matrixRGB(self.globalMaximum)
                matrixData = self.appController.matrixData()
                waves = self.appController.waves(int(self.le_laser.text()))

                self.createPlotRGB()
                self.createPlotSpectrum()
                self.setRangeToWave()
                self.updateSpectrumPlot(waves, matrixData)
                self.updateRGBPlot(matrixRGB)
            except Exception as e:
                print(f"error:{e}")
                self.errorLaser()
    # Capture Controls

    # Background Controls

    # Info Laser

    # Acquisition Settings
    def sweepDirectionSame(self):
        direction = "same"
        pass # call le changement de variable Justine

    def sweepDirectionOther(self):
        direction = "other"
        pass # call le changement de variable Justine

    def setAcquisitionTime(self):
            acqTime = self.sb_acqTime.value()
            pass # Call fonction Justine
            # set 'movingIntegrationData', None
            # launch setIntegrationTime()

    def setExposureTime(self):
            exposureTime = self.sb_exposure.value()
            pass # Call fonction Justine
            # launch setExposureTime()

    def setStep(self):
            step = self.sb_step.value()
            pass # Call fonction Justine

    def set_measure_unit(self):
        if self.cmb_measureUnit.currentText() == 'mm':
            stepMeasureUnit = 10**3

        elif self.cmb_measureUnit.currentText() == 'um':
            stepMeasureUnit = 1

        elif self.cmb_measureUnit.currentText() == 'nm':
            stepMeasureUnit = 10**(-3)

        pass # Call fonction Justine




    # Acquisition Control

    def acquireBackground(self):
        pass # Justine s'en occupe

    def launchAcquisition(self):
        pass # Justine s'en occupe

    def stopAcquisition(self):
        pass # Justine s'en occupe

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

            else:
                self.mousePositionX = positionX
                self.mousePositionY = positionY
                matrixData = self.appController.matrixData()
                waves = self.appController.waves(int(self.le_laser.text()))
                self.updateSpectrumPlot(waves, matrixData)
        except Exception:
            pass

    def setMaximum(self):
        if self.cmb_set_maximum.currentIndex() == 0:
            self.globalMaximum = True
        else:
            self.globalMaximum = False
        self.appController.loadData(self.folderPath)
        matrixRGB = self.appController.matrixRGB(self.globalMaximum)
        matrixData = self.appController.matrixData()
        waves = self.appController.waves(int(self.le_laser.text()))
        self.updateRGBPlot(matrixRGB)

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
        waves = self.appController.waves(int(self.le_laser.text()))

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

    def errorLaser(self):
        self.le_laser.setStyleSheet("background-color: rgb(255, 0, 0)")
        QTimer.singleShot(50, lambda: self.le_laser.setStyleSheet("background-color: rgb(200, 200, 200)"))

    def updateRGBPlot(self, matrixRGB):
        vb = pg.ImageItem(image=matrixRGB)
        self.plotViewBox.addItem(vb)

    def updateSpectrumPlot(self, waves, matrixData):
        # Set the maximum to see the RGB limits and the spectrum clearly
        spectrum = self.appController.spectrum(self.mousePositionX, self.mousePositionY)
        try:
            maximum = max(spectrum)
            minimum = min(spectrum) - 1
        except Exception as e:
            maximum = 1
            minimum = 0

        wavesLen = len(waves)
        colorValues = self.currentSliderValues()

        if self.colorRangeViewEnable:
            # Set the position of the RGB limits
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
            self.plotBlack.setData(waves, np.full(self.dataLen, minimum), pen=(0, 0, 0))

        if not self.colorRangeViewEnable:
            self.plotRedRange.setData(self.waves, np.full(self.dataLen, minimum), pen=(0, 0, 0))
            self.plotGreenRange.setData(self.waves, np.full(self.dataLen, minimum), pen=(0, 0, 0))
            self.plotBlueRange.setData(self.waves, np.full(self.dataLen, minimum), pen=(0, 0, 0))
            self.plotBlack.setData(self.waves, np.full(self.dataLen, minimum), pen=(0, 0, 0))

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
                matrixRGB = self.appController.matrixRGB(self.globalMaximum)
                matrixData = self.appController.matrixData()
                waves = self.appController.waves(int(self.le_laser.text()))
                self.updateSpectrumPlot(waves, matrixData)
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
            matrixData = self.appController.matrixData()
            waves = self.appController.waves(int(self.le_laser.text()))
            self.updateSpectrumPlot(waves, matrixData)
        except Exception:
            pass