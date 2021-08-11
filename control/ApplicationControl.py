import copy
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
        self.spec = None

        self.isLoopRGB = False
        self.quitLoopRGB = True
        notif().addObserver(self, self.react, "Single acquisition done")
        notif().addObserver(self, self.acquisitionDone, "Map acquisition done or interrupted.")

    def react(self, notification):
        point_x = notification.userInfo["point_x"]
        point_y = notification.userInfo["point_y"]
        spectrum = notification.userInfo["spectrum"]

        self.addSpectrum(point_x, point_y, spectrum)
        self.saveThread = Thread(target=self.savePixel, args=(point_x, point_y, spectrum))
        self.saveThread.start()
        # self.savePixel(point_x, point_y, spectrum)

    def matrixRGB(self, globalMaximum=True, VWB=True):
        width, height = self.windowControl.dimensionImage()
        colorValues = self.windowControl.currentSliderValues()
        with self.lock:
            if VWB:
                data = self.HSI.data
            else:
                data = self.HSI.dataWithoutBackground()
        matrixRGB = self.HSI.matrixRGB(data, colorValues, globalMaximum, width, height)
        return matrixRGB

    def waves(self, laser):
        with self.lock:
            wavelength = self.HSI.wavelength
        if self.windowControl.waveNumber:
            waves = self.HSI.waveNumber(wavelength, laser)
        else:
            waves = self.HSI.wavelength
        return waves

    # def loadData(self, path):
    #     with self.lock:
    #         self.HSI.loadData(path)

    def spectrum(self, x, y, VWB=True):
        with self.lock:
            if VWB:
                spectrum = self.HSI.spectrum(x, y, self.HSI.data)
            else:
                spectrum = self.HSI.spectrum(x, y, self.HSI.data)
                background = self.HSI.background
                spectrum = spectrum - background
        return spectrum

    def deleteSpectra(self):
        with self.lock:
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
        try:
            self.Model.width = width
        except Exception as e:
            e = str(e)
            if e == "'NoneType' object is not subscriptable":
                e = "No sutter connected"
            self.windowControl.createErrorDialogs(e)

    def setHeight(self, height):
        try:
            self.Model.height = height
        except Exception as e:
            e = str(e)
            if e == "'NoneType' object is not subscriptable":
                e = "No sutter connected"
            self.windowControl.createErrorDialogs(e)

    def setStep(self, step):
        try:
            self.Model.step = step
        except Exception as e:
            self.windowControl.createErrorDialogs(e)

    def setMeasureUnit(self, measureUnit):
        try:
            self.Model.stepMeasureUnit = measureUnit
        except Exception as e:
            self.windowControl.createErrorDialogs(e)

    def setExposureTime(self, exposureTime):
        try:
            self.Model.exposureTime = exposureTime
        except Exception as e:
            self.windowControl.createErrorDialogs(e)

    def setIntegrationTime(self, acqTime):
        try:
            self.Model.integrationTime = acqTime
        except Exception as e:
            self.windowControl.createErrorDialogs(e)

    def sweepDirectionSame(self):
        self.Model.setDirectionToDefault()

    def sweepDirectionOther(self):
        self.Model.setDirectionToZigzag()

    def acquireBackground(self):
        # with self.lock:
        #     self.backgroundLoop = Thread(target=self.Model.acquireBackground, name="acquireBackgroundThread")
        # self.backgroundLoop.start()
        # self.backgroundLoop.join()
        self.Model.acquireBackground()
        background = self.Model.backgroundData()
        self.HSI.setBackground(background)
        self.saveBackground()

    def saveBackground(self):
        self.HSI.saveCaptureCSV(data=self.HSI.background)

    def launchAcquisition(self):
        # with self.lock:
        if not self.Model.isAcquiring:
            self.acqLoop = Thread(target=self.Model.begin, name="acquisitionThread")
        else:
            self.windowControl.createErrorDialogs("Acquisition has already started.")
        self.acqLoop.start()
        self.startRefreshRGBLoop()

    def stageConnected(self):
        return self.stage

    def spectroConnected(self):
        if self.spec == None:
            return False
        else:
            return True

    def matrixRGBReplace(self):
        globalMaximum = self.windowControl.globalMaximum
        VWB = self.windowControl.visualWithoutBackground
        matrixRGB = self.matrixRGB(globalMaximum, VWB)
        self.windowControl.updateRGBPlot(matrixRGB)

    def addSpectrum(self, x, y, spectrum):
        with self.lock:
            self.HSI.addSpectrum(x, y, spectrum)

    def savePixel(self, x, y, spectrum):
        with self.lock:
            spec = spectrum
        self.HSI.saveCaptureCSV(data=spec, countHeight=y, countWidth=x)

    def stopAcquisition(self):
        with self.lock:
            self.quitLoopRGB = True
            self.isLoopRGB = False
        if self.Model.isAcquiring:
            notif().postNotification("Interrupt acquisition", self)
        else:
            self.windowControl.createErrorDialogs("Mapping already stopped.")

    def acquisitionDone(self, notification):
        with self.lock:
            self.quitLoopRGB = True
            self.isLoopRGB = False
        self.windowControl.acquisitionDone()

    def getFileName(self):
        fileName = self.windowControl.fileName()
        return fileName

    def getLaser(self):
        laser = self.HSI.laser
        return laser

    # thread
    def startRefreshRGBLoop(self):
        with self.lock:
            if not self.isLoopRGB:
                self.quitLoopRGB = False
            else:
                raise RuntimeError("RefreshRGBLoop is already running")
        self.loopRGB = Thread(target=self.refreshRGBLoop, name="refreshRGBLoop")
        self.loopRGB.start()

    def refreshRGBLoop(self):
        self.isLoopRGB = True
        with self.lock:
            quit = self.quitLoopRGB
        while not quit:
            with self.lock:
                quit = self.quitLoopRGB
            self.matrixRGBReplace()
            time.sleep(1)

    # TODO
    def listStageDevices(self) -> list:  # connected
        self.stageDevices = []  # TODO find list from hardware...
        self.stageDevices.insert(0, "Debug")
        self.stageDevices.append("real Sutter")
        devices = []
        for stage in self.stageDevices:
            devices.append(str(stage))
        return devices

    def listSpecDevices(self) -> list:  # connected
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
            self.spec = Mock.MockSpectrometer()
        else:
            self.spec = sb.Spectrometer(self.spectroLink)
        if self.spec is None:
            raise Exception('The spectrometer is not connected!')
        self.Model.connectSpec(self.spec)
        wave = self.Model.wavelengths()
        return wave

    def connectLight(self, index):
        if index == 0:
            self.spec._source = "halogen"
        elif index == 1:
            self.spec._source = "random"

