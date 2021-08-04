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
        colorValues = self.windowController.currentSliderValues()
        if VWB == True:
            data = self.HSI.data
        else:
            data =self.HSI.dataWithoutBackground()
        matrixRGB = self.HSI.matrixRGB(data, colorValues, globalMaximum)
        return matrixRGB

    def waves(self, laser):
        if self.windowController.waveNumber == True:
            waves = self.HSI.waveNumber(laser)
        else:
            waves = self.HSI.wavelength
        return waves

    def loadData(self, path):
        self.HSI.loadData(path)
        colorValues = self.windowController.currentSliderValues()

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




