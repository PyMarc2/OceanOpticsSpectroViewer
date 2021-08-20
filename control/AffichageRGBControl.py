import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from model.HyperSpectralImage import HyperSpectralImage

class AppliControl():
    def __init__(self):
        self.hsi = HyperSpectralImage(createTempFolder=False)
        self.windowControl = None

    def deleteBackground(self):
        self.hsi.deleteBackground()

    def deleteSpectra(self):
        self.hsi.deleteSpectra()

    def deleteWaves(self):
        self.hsi.deleteWavelength()

    def width(self):
        width = self.hsi.widthImage()
        return width

    def height(self):
        height = self.hsi.heightImage()
        return height

    def loadData(self, path):
        foundBackground = self.hsi.loadData(path)
        self.hsi.folderPath = path
        return foundBackground

    def matrixRGB(self, globalMaximum=True, subtractBackground=False):
        colorValues = self.windowControl.currentSliderValues()
        matrixRGB = self.hsi.matrixRGB(colorValues, globalMaximum, subtractBackground=subtractBackground)
        return matrixRGB

    def saveImage(self, matrixRGB):
        self.hsi.saveImage(matrixRGB)

    def saveWithoutBackground(self):
        self.hsi.saveDataWithoutBackground(alreadyWaveNumber=True)

    def spectrum(self, x, y, subtractBackground=False):
        spectrum = self.hsi.spectrum(x, y, subtractBackground=subtractBackground)
        return spectrum

    def waves(self):
        waves = self.hsi.wavelength
        return waves
