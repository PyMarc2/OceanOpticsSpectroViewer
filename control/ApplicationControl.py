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

from distutils.dir_util import copy_tree

class AppControl():
    def __init__(self):
        self.HSI = HyperSpectralImage()
        self.Model = Model()
        self.windowControl = None

        self.stageDevices = []  # find list from hardware...  # TODO
        self.listStageDevices()
        self.stageLink = self.stageDevices[0]

        self.specDevices = []
        self.listSpecDevices()
        self.spectroLink = self.specDevices[0]
        self.lock = Lock()
        self.stage = False
        self.spectro = None

        self.tempFolder = self.HSI.tempFolder
        self.folderPath = ""
        self.fileName = ""

        self.isLoopRGBRunning = False
        self.quitLoopRGB = True
        notif().addObserver(self, self.react, "Single acquisition done")
        notif().addObserver(self, self.acquisitionDone, "Map acquisition done or interrupted.")

    def setFolderPath(self, folderPath):
        """Set the folder path.
        Args:
            folderPath(str): The folder path to add to data.
        """
        if type(folderPath) is not str:
            raise TypeError("folderpath argument is not a string.")
        self.folderPath = folderPath
        path = self.folderPath + "/tempDirectoryPath.txt"
        if os.path.exists(path):
            os.remove(path)
        with open(path, "w+") as f:
            f.write(f"{self.tempFolder}")

    def setFileName(self, fileName):
        """Set the file name.
        Args:
            fileName(str): The file name to add to data.
        """
        if type(fileName) is not str:
            raise TypeError("file name argument is not a string.")
        self.fileName = fileName

    def react(self, notification):
        pointX = notification.userInfo["point_x"]
        pointY = notification.userInfo["point_y"]
        spectrum = notification.userInfo["spectrum"]

        self.saveThread = Thread(target=self.HSI.addSpectrum, args=(pointX, pointY, spectrum))
        self.saveThread.start()

    def matrixRGB(self, globalMaximum=True, subtractBackground=False):
        width, height = self.windowControl.dimensionImage()
        colorValues = self.windowControl.currentSliderValues()
        with self.lock:
            matrixRGB = self.HSI.matrixRGB(colorValues, globalMaximum, width, height, subtractBackground)
        return matrixRGB

    def waves(self):
        with self.lock:
            if self.windowControl.waveNumber:
                waves = self.HSI.waveNumber()
            else:
                waves = self.HSI.wavelength
        return waves

    # def loadData(self, path):
    #     with self.lock:
    #         self.HSI.loadData(path)

    def spectrum(self, x, y, subtractBackground=False):
        with self.lock:
            spectrum = self.HSI.spectrum(x, y, subtractBackground)
        return spectrum

    def deleteSpectra(self):
        with self.lock:
            self.HSI.deleteSpectra()

    def backgroundData(self):
        background = self.HSI.background
        return background

    def setWavelength(self, waves):
        self.HSI.setWavelength(waves)

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
        self.Model.integrationTime = acqTime

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
        if self.spectro == None:
            return False
        else:
            return True

    def matrixRGBReplace(self):
        globalMaximum = self.windowControl.globalMaximum
        subtractBackground = self.windowControl.subtractBackground
        matrixRGB = self.matrixRGB(globalMaximum, subtractBackground)
        self.windowControl.updateRGBPlot(matrixRGB)

    def addSpectrum(self, x, y, spectrum):
        with self.lock:
            self.HSI.addSpectrum(x, y, spectrum)

    def stopAcquisition(self):
        with self.lock:
            self.quitLoopRGB = True
            self.isLoopRGBRunning = False
        if self.Model.isAcquiring:
            notif().postNotification("Interrupt acquisition", self)
        else:
            self.windowControl.createErrorDialogs("Mapping already stopped.")

    def acquisitionDone(self, notification):
        with self.lock:
            self.quitLoopRGB = True
            self.isLoopRGBRunning = False
        self.windowControl.acquisitionDone()
        self.copyDataToFolderPath()


    def getFileName(self):
        return self.fileName

    def getLaser(self):
        laser = self.HSI.laser
        return laser

    # thread
    def startRefreshRGBLoop(self):
        with self.lock:
            if not self.isLoopRGBRunning:
                self.quitLoopRGB = False
            else:
                raise RuntimeError("RefreshRGBLoop is already running")
        self.loopRGB = Thread(target=self.refreshRGBLoop, name="refreshRGBLoop")
        self.loopRGB.start()

    def refreshRGBLoop(self):
        self.isLoopRGBRunning = True
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
        for spectro in self.specDevices:
            devices.append(str(spectro))
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
            self.spectro = Mock.MockSpectrometer()
        else:
            self.spectro = sb.Spectrometer(self.spectroLink)
        if self.spectro is None:
            raise Exception('The spectrometer is not connected!')
        self.Model.connectSpec(self.spectro)
        wave = self.Model.wavelengths()
        return wave

    def connectLight(self, index):
        if index == 0:
            self.spectro._source = "halogen"
        elif index == 1:
            self.spectro._source = "random"

    def saveBackground(self):
        self.HSI.saveSpectrum(self.tempFolder, self.fileName)
        self.copyDataToFolderPath()

    def saveImage(self, matrixRGB):
        self.HSI.saveAsImage(matrixRGB, self.tempFolder, self.fileName)
        self.copyDataToFolderPath()

    def saveWithoutBackground(self):
        self.HSI.saveSpectraWithoutBackground(self.folderPath, self.fileName)

    def copyDataToFolderPath(self):
        copy_tree(f"{self.tempFolder}", f"{self.folderPath}")

