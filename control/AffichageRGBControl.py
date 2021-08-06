import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from model.HyperSpectralImage import HyperSpectralImage

class AppliControl():
    def __init__(self):
        self.hsi = HyperSpectralImage()
        self.windowControl = None

    def matrixData(self):
        matrixData = self.hsi.matrixData(self.hsi.data)
        return matrixData

    def matrixRGB(self, globalMaximum=True):
        colorValues = self.windowControl.currentSliderValues()
        matrixRGB = self.hsi.matrixRGB(self.hsi.data, colorValues, globalMaximum)
        return matrixRGB

    def waves(self):
        waves = self.hsi.wavelength
        return waves

    def loadData(self, path):
        self.hsi.loadData(path)
        colorValues = self.windowControl.currentSliderValues()

    def spectrum(self, x, y):
        spectrum = self.hsi.spectrum(x, y, self.hsi.data)
        return spectrum

    def deleteSpectra(self):
        self.hsi.deleteSpectra()

    def width(self):
        width = self.hsi.widthImage(self.hsi.data)
        return width

    def height(self):
        height = self.hsi.heightImage(self.hsi.data)
        return height




