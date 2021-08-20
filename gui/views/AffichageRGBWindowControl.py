from PyQt5.QtCore import pyqtSignal, Qt, QThreadPool, QThread, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5 import uic

import pyqtgraph as pg

from tkinter.filedialog import askopenfile
import matplotlib.pyplot as plt
from typing import NamedTuple
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

class ColorValues(NamedTuple):
    lowRed: int = None
    highRed: int = None
    lowGreen: int = None
    highGreen: int = None
    lowBlue: int = None
    highBlue: int = None

class WindowControl(QWidget, Ui_MainWindow):
    def __init__(self, model=None):
        super(WindowControl, self).__init__()
        self.setupUi(self)
        self.model = model
        self.appControl = None

        self.sliderPositionIsSet = False
        self.globalMaximum = True
        self.subtractBackground = False

        self.mousePositionX = 0
        self.mousePositionY = 0

        self.rangeLen = 1024
        self.minWave = 0

        self.connectWidgets()
        self.updateSliderStatus()

    def connectWidgets(self):
        self.cmb_set_maximum.currentIndexChanged.connect(self.setMaximum)

        self.cb_subtractbg.stateChanged.connect(self.subtractBg)

        self.graph_rgb.scene().sigMouseMoved.connect(self.mouseMoved)

        self.pb_search.clicked.connect(self.selectSaveFolder)
        self.pb_saveImage.clicked.connect(self.saveImage)
        self.pb_saveWithoutBg.clicked.connect(self.saveWithoutBackground)

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

    def currentSliderValues(self):
        lowRedValue = self.dSlider_red.get_left_thumb_value() / 1024
        highRedValue = self.dSlider_red.get_right_thumb_value() / 1024
        lowGreenValue = self.dSlider_green.get_left_thumb_value() / 1024
        highGreenValue = self.dSlider_green.get_right_thumb_value() / 1024
        lowBlueValue = self.dSlider_blue.get_left_thumb_value() / 1024
        highBlueValue = self.dSlider_blue.get_right_thumb_value() / 1024
        return ColorValues(lowRedValue, highRedValue, lowGreenValue, highGreenValue, lowBlueValue, highBlueValue)

    def mappingOnSlider(self, value):
        return round(((value - self.minWave)/self.rangeLen) * 1024)

    def mappingOnSpinBox(self, value):
        return round((value * self.rangeLen) + self.minWave)

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
                self.updateSpectrumPlot(waves)
        except Exception as e:
            pass

    def saveImage(self):
        matrixRGB = self.appControl.matrixRGB(self.globalMaximum, self.subtractBackground)
        self.appControl.saveImage(matrixRGB)

    def saveWithoutBackground(self):
        self.appControl.saveWithoutBackground()

    def setMaximum(self):
        if self.cmb_set_maximum.currentIndex() == 0:
            self.globalMaximum = True
        else:
            self.globalMaximum = False
        matrixRGB = self.appControl.matrixRGB(self.globalMaximum, self.subtractBackground)
        waves = self.appControl.waves()
        self.updateRGBPlot(matrixRGB)

    def setColorRange(self):
        colorValues = self.currentSliderValues()
        self.sb_lowRed.setValue(self.mappingOnSpinBox(colorValues.lowRed))
        self.sb_highRed.setValue(self.mappingOnSpinBox(colorValues.highRed))
        self.sb_lowGreen.setValue(self.mappingOnSpinBox(colorValues.lowGreen))
        self.sb_highGreen.setValue(self.mappingOnSpinBox(colorValues.highGreen))
        self.sb_lowBlue.setValue(self.mappingOnSpinBox(colorValues.lowBlue))
        self.sb_highBlue.setValue(self.mappingOnSpinBox(colorValues.highBlue))

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

        self.sb_lowRed.setValue(self.mappingOnSpinBox(colorValues.lowRed))
        self.sb_highRed.setValue(self.mappingOnSpinBox(colorValues.highRed))
        self.sb_lowGreen.setValue(self.mappingOnSpinBox(colorValues.lowGreen))
        self.sb_highGreen.setValue(self.mappingOnSpinBox(colorValues.highGreen))
        self.sb_lowBlue.setValue(self.mappingOnSpinBox(colorValues.lowBlue))
        self.sb_highBlue.setValue(self.mappingOnSpinBox(colorValues.highBlue))

        self.updateSliderStatus()

    def selectSaveFolder(self):
        try:
            folderPath = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
            self.appControl.deleteSpectra()
            self.appControl.deleteBackground()
            self.appControl.deleteWaves()
            self.appControl.setFolderPath(folderPath)
            foundBackground = self.appControl.loadData()
            self.subtractBackground = False
            matrixRGB = self.appControl.matrixRGB(self.globalMaximum, self.subtractBackground)
            waves = self.appControl.waves()

            self.mousePositionY = 0
            self.mousePositionX = 0
            self.createPlotRGB()
            self.createPlotSpectrum()
            self.setRangeToWave()
            self.updateSpectrumPlot(waves)
            self.updateRGBPlot(matrixRGB)
            self.pb_saveImage.setEnabled(True)
            self.pb_saveImage.setStyleSheet("")
            if foundBackground:
                self.pb_saveWithoutBg.setEnabled(True)
                self.pb_saveWithoutBg.setStyleSheet("")
                self.cb_subtractbg.setEnabled(True)
            elif not foundBackground:
                self.pb_saveWithoutBg.setEnabled(False)
                self.pb_saveWithoutBg.setStyleSheet("background-color: rgb(42, 42, 42);")
                self.cb_subtractbg.setCheckState(False)
                self.cb_subtractbg.setEnabled(False)
        except Exception as e:
            pass

    def subtractBg(self):
        if self.cb_subtractbg.checkState() == 2:
            self.subtractBackground = True
        if self.cb_subtractbg.checkState() == 0:
            self.subtractBackground = False
        matrixRGB = self.appControl.matrixRGB(self.globalMaximum, self.subtractBackground)
        waves = self.appControl.waves()
        self.updateSpectrumPlot(waves)
        self.updateRGBPlot(matrixRGB)

    def updateRGBPlot(self, matrixRGB):
        matrixRGB = matrixRGB.transpose(1, 0, 2)
        vb = pg.ImageItem(image=matrixRGB)
        self.plotViewBox.addItem(vb)

    def updateSpectrumPlot(self, waves):
        spectrum = self.appControl.spectrum(self.mousePositionX, self.mousePositionY, self.subtractBackground)
        try:
            maximum = max(spectrum)
            minimum = min(spectrum) - 1
        except Exception as e:
            maximum = 1
            minimum = 0

        wavesLen = len(waves)
        colorValues = self.currentSliderValues()

        # Set the position of the RGB limits
        lowRed = int( colorValues.lowRed * wavesLen )
        highRed = int( colorValues.highRed * wavesLen - 1 )
        lowGreen = int( colorValues.lowGreen * wavesLen )
        highGreen = int( colorValues.highGreen * wavesLen - 1 )
        lowBlue = int( colorValues.lowBlue * wavesLen )
        highBlue = int( colorValues.highBlue * wavesLen - 1 )

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

        if self.sliderPositionIsSet:
            try:
                matrixRGB = self.appControl.matrixRGB(self.globalMaximum, self.subtractBackground)
                waves = self.appControl.waves()
                self.updateSpectrumPlot(waves)
                self.updateRGBPlot(matrixRGB)

            except:
                pass
        else:
            self.sliderPositionIsSet = True
