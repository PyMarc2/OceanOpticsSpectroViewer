import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from model.HyperSpectralImage import HyperSpectralImage

class AppControl():
    def __init__(self):
        self.HSI = HyperSpectralImage()
        self.windowControl = None
        self.microControl = None

    def matrixRGB(self, globalMaximum=True, VWB=True):
        colorValues = self.windowControl.currentSliderValues()
        if VWB == True:
            data = self.HSI.data
        else:
            data =self.HSI.dataWithoutBackground()
        matrixRGB = self.HSI.matrixRGB(data, colorValues, globalMaximum)
        return matrixRGB

    def waves(self, laser):
        if self.windowControl.waveNumber == True:
            waves = self.HSI.waveNumber(laser)
        else:
            waves = self.HSI.wavelength
        return waves

    def loadData(self, path):
        self.HSI.loadData(path)
        colorValues = self.windowControl.currentSliderValues()

    def spectrum(self, x, y, VWB=True):
        if VWB == True:
            spectrum = self.HSI.spectrum(x, y, self.HSI.data)
        else:
            spectrum = self.HSI.spectrum(x, y, self.HSI.data)
            background = self.HSI.background
            spectrum = spectrum - background
        return spectrum

    def deleteSpectrum(self):
        self.HSI.deleteSpectrum()

    def backgroundData(self):
        background = self.HSI.background
        return background

    def setWavelength(self, waves):
        self.HSI.setWavelength(waves)

    def saveImage(self, matrixRGB):
        self.HSI.saveImage(matrixRGB)

    def connectDetection(self, index):
        waves = self.microControl.connectDetection(index)
        return waves

    def connectStage(self, index):
        self.microControl.connectStage(index)

    def setFolderPath(self, folderPath):
        self.HSI.setFolderPath(folderPath)

    def save(self):
        #pas fini
        fileName = self.windowControl.fileName()
        self.HSI.setFileName(fileName)

    def saveWithoutBackground(self):
        self.HSI.saveDataWithoutBackground()

    def setWidth(self, width):
        self.microControl.setWidth(width)

    def setHeight(self, height):
        self.microControl.setHeight(height)

    def setStep(self, step):
        self.microControl.setStep(step)

    def setMeasureUnit(self, measureUnit):
        self.microControl.setStepMeasureUnit(measureUnit)

    def setExposureTime(self, exposureTime):
        self.microControl.setExposureTime(exposureTime)

    def setIntegrationTime(self, acqTime):
        self.microControl.setIntegrationTime(acqTime)

    def sweepDirectionSame(self):
        self.microControl.setDirectionToDefault()

    def sweepDirectionOther(self):
        self.microControl.setDirectionToZigzag()

    def acquireBackground(self):
        background = self.microControl.acquireBackground()
        self.HSI.setBackground(background)

    def saveBackground(self):
        self.HSI.saveCaptureCSV(self.HSI.background)

    def launchAcquisition(self):
        self.microControl.begin()

    def allConnected(self, indexStage, indexSpectro):
        stage = self.microControl.getStage(indexStage)
        spectro = self.microControl.getSpectro(indexSpectro)
        if stage and spectro:
            return True
        else:
            return False

    def matrixRGBReplace(self):
        globalMaximum = self.windowControl.globalMaximum
        VWB = self.windowControl.visualWithoutBackground
        matrixRGB = self.matrixRGB(globalMaximum, VWB)
        self.windowControl.updateRGBPlot(matrixRGB)

    def addSpectrum(self, x, y, spectrum):
        self.HSI.addSpectrum(x, y, spectrum)

    def savePixel(self, x, y, spectrum):
        self.HSI.saveCaptureCSV(data=spectrum, countHeight=y, countWidth=x)

    def stopAcquisition(self):
        self.microControl.stopAcq()

    def getStageList(self):
        stageList = self.microControl.getStageList()
        return stageList

    def getSpectroList(self):
        spectroList = self.microControl.getSpecList()
        return spectroList







