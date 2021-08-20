import numpy as np
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from model.HyperSpectralImage import HyperSpectralImage

class AppliControl():
    def __init__(self):
        self.hsi = HyperSpectralImage(createTempFolder=False)
        self.windowControl = None
        self.folderPath = ""

    def setFolderPath(self, folderPath):
        """Set the folder path.
        Args:
            folderPath(str): The folder path to add to data.
        """
        if type(folderPath) is not str:
            raise TypeError("folderpath argument is not a string.")
        self.folderPath = folderPath

    def deleteBackground(self):
        self.hsi.deleteBackground()

    def deleteSpectra(self):
        self.hsi.deleteSpectra()

    def deleteWaves(self):
        self.hsi.deleteWavelength()

    def loadData(self):
        foundBackground = self.hsi.loadSpectra(self.folderPath)
        return foundBackground

    def matrixRGB(self, globalMaximum=True, subtractBackground=False):
        colorValues = self.windowControl.currentSliderValues()
        matrixRGB = self.hsi.matrixRGB(colorValues, globalMaximum, subtractBackground=subtractBackground)
        return matrixRGB

    def saveImage(self, matrixRGB):
        self.hsi.saveAsImage(matrixRGB, self.folderPath, "")

    def saveWithoutBackground(self):
        self.hsi.saveSpectraWithoutBackground(self.folderPath, "spectrum", alreadyWaveNumber=True)

    def spectrum(self, x, y, subtractBackground=False):
        spectrum = self.hsi.spectrum(x, y, subtractBackground=subtractBackground)
        return spectrum

    def waves(self):
        waves = self.hsi.wavelength
        return waves
