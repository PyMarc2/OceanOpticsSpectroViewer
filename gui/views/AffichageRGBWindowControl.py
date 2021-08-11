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

UiPath = os.path.dirname(os.path.realpath(__file__)) + '{0}AffichageRGBUi.ui'.format(os.sep)
Ui_MainWindow, QtBaseClass = uic.loadUiType(UiPath)

class WindowControl(QWidget, Ui_MainWindow):
    def __init__(self, model=None):
        super(WindowControl, self).__init__()
        self.setupUi(self)
        self.model = model
        self.appControl = None

        self.doSliderPositionAreInitialize = False
        self.globalMaximum = True
        self.folderpath = ""
        self.doNotSubtractBg = True

        self.mousePositionX = 0
        self.mousePositionY = 0

        self.rangeLen = 1024
        self.minWave = 0

        self.connectWidgets()
        self.updateSliderStatus()

    def connectWidgets(self):
        self.cmb_set_maximum.currentIndexChanged.connect(self.setMaximum)

        self.cb_subtractbg.stateChanged.connect(self.subtractBackground)

        self.graph_rgb.scene().sigMouseMoved.connect(self.mouseMoved)
        self.pb_search.clicked.connect(self.selectSaveFolder)
        self.pb_saveImage.clicked.connect(self.saveImage)

        self.dSlider_red.valueChanged.connect(self.setColorRange)
        self.dSlider_green.valueChanged.connect(self.setColorRange)
        self.dSlider_blue.valueChanged.connect(self.setColorRange)

        self.sb_highRed.valueChanged.connect(self.updateSliderStatus)
        self.sb_lowRed.valueChanged.connect(self.updateSliderStatus)
        self.sb_highGreen.valueChanged.connect(self.updateSliderStatus)
        self.sb_lowGreen.valueChanged.connect(self.updateSliderStatus)
        self.sb_highBlue.valueChanged.connect(self.updateSliderStatus)
        self.sb_lowBlue.valueChanged.connect(self.updateSliderStatus)

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

            width = self.appControl.width()
            height = self.appControl.height()

            if positionX <= -1 or positionY <= -1:
                pass

            elif positionX >= width:
                pass

            elif positionY >= height:
                pass

            else:
                self.mousePositionX = positionX
                self.mousePositionY = positionY
                waves = self.appControl.waves()
                matrixData = self.appControl.matrixData(self.doNotSubtractBg)
                self.updateSpectrumPlot(waves, matrixData)
        except Exception as e:
            pass

    def setMaximum(self):
        if self.cmb_set_maximum.currentIndex() == 0:
            self.globalMaximum = True
        else:
            self.globalMaximum = False
        self.appControl.loadData(self.folderPath)
        matrixRGB = self.appControl.matrixRGB(self.globalMaximum, self.doNotSubtractBg)
        matrixData = self.appControl.matrixData(self.doNotSubtractBg)
        waves = self.appControl.waves()
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
        waves = self.appControl.waves()

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

    def selectSaveFolder(self):
        try:
            self.folderPath = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
            self.appControl.deleteSpectra()
            self.appControl.loadData(self.folderPath)
            matrixRGB = self.appControl.matrixRGB(self.globalMaximum, self.doNotSubtractBg)
            matrixData = self.appControl.matrixData(self.doNotSubtractBg)
            waves = self.appControl.waves()

            self.createPlotRGB()
            self.createPlotSpectrum()
            self.setRangeToWave()
            self.updateSpectrumPlot(waves, matrixData)
            self.updateRGBPlot(matrixRGB)
            self.pb_saveImage.setEnabled(True)
            self.pb_saveImage.setStyleSheet("")
        except:
            pass

    def saveImage(self):
        matrixRGB = self.appControl.matrixRGB(self.globalMaximum, self.doNotSubtractBg)
        self.appControl.saveImage(matrixRGB)

    def updateRGBPlot(self, matrixRGB):
        matrixRGB = matrixRGB.transpose(1, 0, 2)
        vb = pg.ImageItem(image=matrixRGB)
        self.plotViewBox.addItem(vb)

    def updateSpectrumPlot(self, waves, matrixData):
        # Set the maximum to see the RGB limits and the spectrum clearly
        spectrum = self.appControl.spectrum(self.mousePositionX, self.mousePositionY)
        try:
            maximum = max(spectrum)
            minimum = min(spectrum) - 1
        except Exception as e:
            maximum = 1
            minimum = 0

        wavesLen = len(waves)
        colorValues = self.currentSliderValues()

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
        self.plotBlack.setData(waves, np.full(wavesLen, minimum), pen=(0, 0, 0))
        self.plotSpectrum.setData(waves, spectrum)

        self.le_x.setText(str(self.mousePositionX))
        self.le_y.setText(str(self.mousePositionY))

    def updateSliderStatus(self):
        self.dSlider_red.set_left_thumb_value(self.mappingOnSlider(self.sb_lowRed.value()))
        self.dSlider_red.set_right_thumb_value(self.mappingOnSlider(self.sb_highRed.value()))
        self.dSlider_green.set_left_thumb_value(self.mappingOnSlider(self.sb_lowGreen.value()))
        self.dSlider_green.set_right_thumb_value(self.mappingOnSlider(self.sb_highGreen.value()))
        self.dSlider_blue.set_left_thumb_value(self.mappingOnSlider(self.sb_lowBlue.value()))
        self.dSlider_blue.set_right_thumb_value(self.mappingOnSlider(self.sb_highBlue.value()))

        if self.doSliderPositionAreInitialize:
            try:
                matrixRGB = self.appControl.matrixRGB(self.globalMaximum, self.doNotSubtractBg)
                matrixData = self.appControl.matrixData(self.doNotSubtractBg)
                waves = self.appControl.waves()
                self.updateSpectrumPlot(waves, matrixData)
                self.updateRGBPlot(matrixRGB)

            except:
                pass
        else:
            self.doSliderPositionAreInitialize = True

    def subtractBackground(self):
        if self.cb_subtractbg.checkState() == 2:
            self.doNotSubtractBg = False
        if self.cb_subtractbg.checkState() == 0:
            self.doNotSubtractBg = True
        matrixRGB = self.appControl.matrixRGB(self.globalMaximum, self.doNotSubtractBg)
        matrixData = self.appControl.matrixData(self.doNotSubtractBg)
        waves = self.appControl.waves()
        self.updateSpectrumPlot(waves, matrixData)
        self.updateRGBPlot(matrixRGB)
