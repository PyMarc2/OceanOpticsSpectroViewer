import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from model.HyperSpectralImage import HyperSpectralImage

class AppliControl():
    def __init__(self):
        self.hsi = HyperSpectralImage()
        self.windowControl = None

    def deleteBackground(self):
        self.hsi.deleteBackground()

    def deleteSpectra(self):
        self.hsi.deleteSpectra()

    def deleteWaves(self):
        self.hsi.deleteWavelength()

    def height(self):
        height = self.hsi.heightImage(self.hsi.data)
        return height

    def loadData(self, path):
        foundBackground = self.hsi.loadData(path)
        self.hsi.folderPath = path
        return foundBackground

    def matrixData(self, subtractBackground=False):
        if subtractBackground:
            data = self.hsi.dataWithoutBackground()
        else:
            data = self.hsi.data
        matrixData = self.hsi.matrixData(data)
        return matrixData

    def matrixRGB(self, globalMaximum=True, subtractBackground=False):
        colorValues = self.windowControl.currentSliderValues()
        if subtractBackground:
            data = self.hsi.dataWithoutBackground()
        else:
            data = self.hsi.data
        matrixRGB = self.hsi.matrixRGB(data, colorValues, globalMaximum)
        return matrixRGB

    def saveImage(self, matrixRGB):
        self.hsi.saveImage(matrixRGB)

    def saveWithoutBackground(self):
        self.hsi.saveDataWithoutBackground(alreadyWaveNumber=True)

    def spectrum(self, x, y, subtractBackground=False):
        if subtractBackground:
            spectrum = self.hsi.spectrum(x, y, self.hsi.data)
            background = self.hsi.background
            spectrum = spectrum - background
        else:
            spectrum = self.hsi.spectrum(x, y, self.hsi.data)
        return spectrum

    def subtractBackground(self):
        self.hsi.dataWithoutBackground()

    def waves(self):
        waves = self.hsi.wavelength
        return waves

    def width(self):
        width = self.hsi.widthImage(self.hsi.data)
        return width