import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from model.HyperSpectralImage import HyperSpectralImage

class AppliControl():
    def __init__(self):
        self.HSI = HyperSpectralImage()
        self.windowControl = None

    def matrixData(self):
        matrixData = self.HSI.matrixData(self.HSI.data)
        return matrixData

    def matrixRGB(self, globalMaximum=True):
        colorValues = self.windowControl.currentSliderValues()
        matrixRGB = self.HSI.matrixRGB(self.HSI.data, colorValues, globalMaximum)
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

    def spectrum(self, x, y):
        spectrum = self.HSI.spectrum(x, y, self.HSI.data)
        return spectrum

    def deleteSpectrum(self):
        self.HSI.deleteSpectrum()

    def width(self):
        width = self.HSI.widthImage(self.HSI.data)
        return width

    def height(self):
        height = self.HSI.heightImage(self.HSI.data)
        return height





