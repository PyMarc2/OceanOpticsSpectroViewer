import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from model.HyperSpectralImage import HyperSpectralImage
import seabreeze.spectrometers as sb
from threading import *
import time

class AppControl():
    def __init__(self):
        self.HSI = HyperSpectralImage()
        self.windowControl = None
        self.microControl = None

        self.stageDevices = []  # find list from hardware...  # TODO
        self.listStageDevices()
        self.stageLink = self.stageDevices[0]

        self.specDevices = []
        self.listSpecDevices()
        self.spectroLink = self.specDevices[0]
        self.lock = Lock()

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

    def deleteSpectra(self):
        self.HSI.deleteSpectra()

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

    def setFileName(self, fileName):
        self.HSI.setFileName(fileName)

    def saveWithoutBackground(self):
        self.HSI.saveDataWithoutBackground()

    def setLaserWavelength(self, laser):
        self.HSI.setLaserWavelength(laser)

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
        self.HSI.saveCaptureCSV(data=self.HSI.background)

    def launchAcquisition(self):
        self.microControl.begin()

    def stageConnected(self):
        stage = self.microControl.getStage()
        return stage

    def spectroConnected(self):
        spectro = self.microControl.getSpectro()
        return spectro


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

    def getFileName(self):
        fileName = self.windowControl.fileName()
        return fileName

    def getLaser(self):
        laser = self.HSI.laser
        return laser

    # thread

    def startRefreshRGBLoop(self):
        with self.lock:
            if not self.isMonitoring:
                self.quitMonitoring = False
                self.loopRGB = Thread(target=self.refreshRGBLoop, name="refreshRGBLoop")
                self.loopRGB.start()
            else:
                raise RuntimeError("RefreshRGBLoop is already running")

    def refreshRGBLoop(self):
        while self.quitMonitoring == False:
            with self.lock:
                self.matrixRGBReplace()
            time.sleep(3)
            if self.quitMonitoring == True:
                break



    # à faire

    def listStageDevices(self) -> list: # connecté
        self.stageDevices = []  # find list from hardware... # TODO
        self.stageDevices.insert(0, "Debug")
        self.stageDevices.append("real Sutter")
        devices = []
        for stage in self.stageDevices:
            devices.append(str(stage))
        return devices

    def listSpecDevices(self) -> list: # connecté
        self.specDevices = sb.list_devices()
        self.specDevices.insert(0, "MockSpectrometer")
        devices = []
        for spec in self.specDevices:
            devices.append(str(spec))
        return devices

    def connectStage(self, index): # à vérifier DANGER
        self.stageLink = self.stageDevices[index]
        if self.stageLink == "Debug":
            self.stage = sutter.SutterDevice(serialNumber="debug")
            self.stage.initializeDevice()
        else:
            # TODO will update with list provided by sepo.SerialPort.matchPorts(idVendor=4930, idProduct=1)...
            self.stage = sutter.SutterDevice()
            self.stage.initializeDevice()
        if self.stage is None:
            raise Exception('The sutter is not connected!')

    def connectDetection(self, index): # à vérifier DANGER
        self.spectroLink = self.specDevices[index]
        if self.spectroLink == "MockSpectrometer":
            self.spec = Mock.MockSpectrometer()
        else:
            self.spec = sb.Spectrometer(self.spectroLink)
        if self.spec is None:
            raise Exception('The spectrometer is not connected!')








