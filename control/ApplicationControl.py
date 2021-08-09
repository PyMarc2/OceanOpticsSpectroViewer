import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from model.HyperSpectralImage import HyperSpectralImage
import seabreeze.spectrometers as sb
from threading import *
import time
from gui.modules import mockSpectrometer as Mock
from tools.CircularList import RingBuffer
from model.microscopeDevice import Model
import hardwarelibrary.motion.sutterdevice as sutter
from hardwarelibrary.notificationcenter import NotificationCenter as notif

class AppControl():
    def __init__(self):
        self.HSI = HyperSpectralImage()
        self.Model = Model()
        self.windowControl = None
        self.microControl = None

        self.stageDevices = []  # find list from hardware...  # TODO
        self.listStageDevices()
        self.stageLink = self.stageDevices[0]

        self.specDevices = []
        self.listSpecDevices()
        self.spectroLink = self.specDevices[0]
        self.lock = Lock()
        self.stage = False
        self.spec = False

        notif().addObserver(self, self.react, "Single acquisition done", Model)  # TODO add userInfo received

    def react(self, *args):
        # TODO change function name
        # TODO call following functions with dict received as userInfo
        # self.appControl.addSpectrum(point_x, point_y, spectrum)
        # self.appControl.matrixRGBReplace()
        # self.appControl.savePixel(point_x, point_y, spectrum)
        pass

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

    def setFolderPath(self, folderPath):
        self.HSI.setFolderPath(folderPath)

    def setFileName(self, fileName):
        self.HSI.setFileName(fileName)

    def saveWithoutBackground(self):
        self.HSI.saveDataWithoutBackground()

    def setLaserWavelength(self, laser):
        self.HSI.setLaserWavelength(laser)

    def setWidth(self, width):
        self.Model.width = width

    def setHeight(self, height):
        self.Model.height = height

    def setStep(self, step):
        self.Model.step = step

    def setMeasureUnit(self, measureUnit):
        self.Model.stepMeasureUnit = measureUnit

    def setExposureTime(self, exposureTime):
        self.Model.exposureTime = exposureTime

    def setIntegrationTime(self, acqTime):
        try:
            self.Model.integrationTime = acqTime
        except:  # TODO if integrationTime is greater than exposure time
            pass

    def sweepDirectionSame(self):
        self.Model.setDirectionToDefault()

    def sweepDirectionOther(self):
        self.Model.setDirectionToZigzag()

    def acquireBackground(self):
        background = self.Model.acquireBackground()
        self.HSI.setBackground(background)

    def saveBackground(self):
        self.HSI.saveCaptureCSV(data=self.HSI.background)

    def launchAcquisition(self):
        with self.lock:
            if not self.Model.isAcquiring:
                self.acqLoop = Thread(target=self.Model.begin, name="acquisitionThread")
            else:
                self.windowControl.createErrorDialogs("Acquisition has already started.")
        self.acqLoop.start()

    def stageConnected(self):
        return self.stage

    def spectroConnected(self):
        return self.spec

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
        with self.lock:
            self.Model.stopAcq()
            self.acqLoop.quit()

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
            stage = sutter.SutterDevice(serialNumber="debug")
            stage.initializeDevice()
        else:
            # TODO will update with list provided by sepo.SerialPort.matchPorts(idVendor=4930, idProduct=1)...
            stage = sutter.SutterDevice()
            stage.initializeDevice()
        if stage is None:
            raise Exception('The sutter is not connected!')
            self.stage = False
        self.Model.connectStage(stage)
        self.stage = True

    def connectDetection(self, index): # à vérifier DANGER
        self.spectroLink = self.specDevices[index]
        if self.spectroLink == "MockSpectrometer":
            spec = Mock.MockSpectrometer()
        else:
            spec = sb.Spectrometer(self.spectroLink)
        if spec is None:
            raise Exception('The spectrometer is not connected!')
            self.spec = False
        self.Model.connectSpec(spec)
        self.spec = True
        wave = self.Model.wavelengths()
        return wave
