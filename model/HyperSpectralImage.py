import matplotlib.pyplot as plt
from typing import NamedTuple
import pandas as pd
import numpy as np
import tempfile
import fnmatch
import copy
import csv
import os
import re

class ColorValues(NamedTuple): # If you need to use matrixRGB function you need this.
    lowRed: int = None
    highRed: int = None
    lowGreen: int = None
    highGreen: int = None
    lowBlue: int = None
    highBlue: int = None

class DataPoint(NamedTuple):
    x: int = None
    y: int = None
    spectrum: object = None

class HyperSpectralImage:
    def __init__(self,createTempFolder=True):
        self.spectralPoints = []
        self.wavelength = []
        self.background = []
        self.excitationWavelength = None
        self.tempFolder = None
        if createTempFolder:
            self.tempFolder = tempfile.mkdtemp(prefix="microRamanTemporaryData_")

    # Public functions

    def addSpectrum(self, x, y, spectrum, autoSave=True):
        """Add a spectrum to the data.
        Args:
            x(int): Position on the x-axis.
            y(int): Position on the y-axis.
            spectrum(list or numpy.ndarray): Spectrum to add to data.
        """
        if type(x) is not int:
            raise TypeError("x argument is not int.")
        if type(y) is not int:
            raise TypeError("y argument is not int.")
        if type(spectrum) is list:
            spectrum = np.array(spectrum)
        if type(spectrum) is not np.ndarray:
            raise TypeError("spectrum argument is not a list or numpy.ndarray.")
        self.spectralPoints.append(DataPoint(x, y, spectrum))
        if autoSave:
            spectrum = self.spectrum(x, y)
            self.saveSpectrum(self.tempFolder, "spectrum", countWidth=x, countHeight=y)

    def deleteSpectra(self):
        """Delete all spectra."""
        self.spectralPoints = []

    def spectrum(self, x, y, subtractBackground=False):
        """Return a specific spectrum.
        Args:
            x(int): Position on the x-axis.
            y(int): Position on the y-axis.
            [Optional]subtractBackground(bool): Return the spectrum without background.
        Returns:
            spectrum(numpy.ndarray): Spectrum at the specific coordinates.
        """
        if type(x) is not int:
            raise TypeError("x argument is not int.")
        if type(y) is not int:
            raise TypeError("y argument is not int.")
        if type(subtractBackground) is not bool:
            raise TypeError("subtractBackground argument is not a boolean.")

        spectrum = None
        if subtractBackground:
            data = self.spectraWithoutBackground()
            for item in data:
                if item.x == x:
                    if item.y == y:
                        spectrum = item.spectrum
        else:
            for item in self.spectralPoints:
                if item.x == x:
                    if item.y == y:
                        spectrum = item.spectrum
        return spectrum

    def setBackground(self, background):
        """Set the background to data.
        Args:
            background(list or numpy.ndarray): The background.
        """
        if type(background) is list:
            background = np.array(background)
        if type(background) is not np.ndarray:
            raise TypeError("background argument is not a list or numpy.ndarray.")
        self.background = background

    def deleteBackground(self):
        """Delete the background."""
        self.background = []

    def setWavelength(self, wavelength):
        """Set the wavelength to data.
        Args:
            wavelength(list or numpy.ndarray): The wavelength.
        """
        if type(wavelength) is list:
            wavelength = np.array(wavelength)
        if type(wavelength) is not np.ndarray:
            raise TypeError("wavelength argument is not a list or numpy.ndarray.")
        self.wavelength = np.array(wavelength)

    def deleteWavelength(self):
        """Delete the wavelength."""
        self.wavelength = []

    def waveNumber(self):
        """Return the waveNumber.
        Returns:
            waveNumber(numpy.ndarray): The waveNumber.
        """
        if self.excitationWavelength == None:
            raise RuntimeError("self.excitationWavelength is not defined.")
        elif type(self.wavelength) is not np.ndarray:
            raise RuntimeError("self.wavelength is not defined.")
        else:
            waveNumber = ((1 / self.excitationWavelength) - (1 / self.wavelength)) * 10 ** 7
            return waveNumber.round(0)

    def setLaserWavelength(self, excitationWavelength):
        """Set the excitationWavelength wavelength to data.
        Args:
            excitationWavelength(int): The wavelength of the excitation source.
        """
        if type(excitationWavelength) is not int:
            raise TypeError("excitationWavelength argument is not int.")
        self.excitationWavelength = excitationWavelength

    def deleteLaserWavelength(self):
        """delete the excitation wavelength"""
        self.excitationWavelength = None

    def matrixRGB(self, colorValues, globalMaximum=True, width=None, height=None, subtractBackground=False):
        """Return a matrixRGB.
        Args:
            colorValues(namedTuple): Contained 6 values of RGB limits.
                lowRed = ColorValues[0] | highRed = ColorValues[1] | lowGreen = ColorValues[2]
                highGreen = ColorValues[3] | lowBlue = ColorValues[4] | highBlue = ColorValues[5]
            [Optional]globalMaximum(bool): Normalized with the maximum of each pixel if False.
            [Optional]width(int): The width of the matrix.
            [Optional]height(int): the height of the matrix.
            [Optional]subtractBackground(bool): Use the data without background if True.
        Returns:
            matrixRGB(numpy.ndarray): The matrixRGB.
            None(nonetype): If any problem.
        """
        if type(globalMaximum) is not bool:
            raise TypeError("globalMaximum argument is not a boolean.")
        if type(width) is not int:
            if width == None:
                pass
            else:
                raise TypeError("countWidth argument is not int.")
        if type(height) is not int:
            if height == None:
                pass
            else:
                raise TypeError("countHeight argument is not int.")
        if type(subtractBackground) is not bool:
            raise TypeError("subtractBackground argument is not a boolean.")

        try:
            if width == None or height ==None:
                width = self.width()
                height = self.height()
            else:
                pass

            spectrumLen = self.spectrumLen()

            lowRed = round(colorValues.lowRed * spectrumLen)
            highRed = round(colorValues.highRed * spectrumLen)
            lowGreen = round(colorValues.lowGreen * spectrumLen)
            highGreen = round(colorValues.highGreen * spectrumLen)
            lowBlue = round(colorValues.lowBlue * spectrumLen)
            highBlue = round(colorValues.highBlue * spectrumLen)


            matrixRGB = np.zeros((height, width, 3))
            matrix = self.matrixData(width, height, subtractBackground=subtractBackground)

            matrixRGB[:, :, 0] = matrix[:, :, lowRed:highRed].sum(axis=2)
            matrixRGB[:, :, 1] = matrix[:, :, lowGreen:highGreen].sum(axis=2)
            matrixRGB[:, :, 2] = matrix[:, :, lowBlue:highBlue].sum(axis=2)

            if globalMaximum:
                matrixRGB = (matrixRGB / np.max(matrixRGB)) * 255

            else:
                maxima = matrixRGB.max(axis=2)
                maxima = np.dstack((maxima,) * 3)
                np.seterr(divide='ignore', invalid='ignore')
                matrixRGB /= maxima
                matrixRGB[np.isnan(matrixRGB)] = 0
                matrixRGB *= 255

            matrixRGB = matrixRGB.round(0)
            thresholdIndices = matrixRGB < 0
            matrixRGB[thresholdIndices] = 0
            return matrixRGB
        except:
            return None

    def saveAsImage(self, matrixRGB, path, fileName):
        """Save the matrixRGB as a image in png format.
        Args:
            matrixRGB(np.ndarray): The matrixRGB to save as a png.
        Return:
            image(.png): Save in RawData in the folderPath.
        """
        if type(matrixRGB) is not np.ndarray:
            raise TypeError("matrixRGB argument is not a numpy.ndarray.")
        path = path + "/"
        img = matrixRGB.astype(np.uint8)
        if fileName == "":
            plt.imsave(path + "matrixRGB.png", img)
        else:
            plt.imsave(path + fileName + "_matrixRGB.png", img)

    def loadSpectra(self, path):
        """Load the data of a specific repository in the data.
        Args:
            path(str): The path of the repository.
        """
        if type(path) is not str:
            raise TypeError("path argument is not a string.")
        foundBackground = False
        doGetWaveLength = False
        foundFiles = []
        for file in os.listdir(path):
            if fnmatch.fnmatch(file, f'*.csv'):
                foundFiles.append(file)

        sortedPaths = foundFiles
        for name in sortedPaths:
            # Find the positions
            matchCoords = re.match(r"([A-Za-z_]*)_x(\d+)_y(\d+).*", name)
            if matchCoords:
                posX = int(matchCoords.group(2))
                posY = int(matchCoords.group(3))

                # Open file and put in the data
                fich = open(path + '/' + name, "r")
                test_str = list(fich)
                fich.close()
                xAxis = []
                spectrum = []
                for j in test_str:
                    elem_str = j.replace("\n", "")
                    elem = elem_str.split(",")
                    spectrum.append(float(elem[1]))

                    if doGetWaveLength == False:
                        elem_str = j.replace("\n", "")
                        elem = elem_str.split(",")
                        xAxis.append(float(elem[0]))
                        self.setWavelength(xAxis)
                doGetWaveLength = True
                self.addSpectrum(posX, posY, spectrum, autoSave=False)

            matchBackground = re.match(".*?(_background).*", name)
            if matchBackground:
                foundBackground = True
                fich = open(path + '/' + name, "r")
                test_str = list(fich)
                fich.close()
                spectrum = []
                for j in test_str:
                    elem_str = j.replace("\n", "")
                    elem = elem_str.split(",")
                    spectrum.append(float(elem[1]))
                self.background = spectrum

        return foundBackground

    def saveSpectrum(self, path, fileName, countHeight=None, countWidth=None):
        """Save the background or one specific spectrum.
        Args:
            countHeight(int): If the two count are None save the background. Else save a spectrum.
            countWidth(int): If the two count are None save the background. Else save a spectrum.
        Return:
            CSVFile(.csv): Save the file in RawData at the folder path.
        """
        if type(countWidth) is not int:
            if countWidth == None:
                pass
            else:
                raise TypeError("width argument is not int.")
        if type(countHeight) is not int:
            if countHeight == None:
                pass
            else:
                raise TypeError("height argument is not int.")
        newPath = path + "/" + "RawData"
        os.makedirs(newPath, exist_ok=True)
        if countHeight is None and countWidth is None:
            path = os.path.join(newPath, f"{fileName}_background")
            with open(path + ".csv", "w+") as f:
                for i, x in enumerate(self.waveNumber()):
                    f.write(f"{x},{self.background[i]}\n")
                f.close()
        else:
            path = os.path.join(newPath, f"{fileName}_x{countWidth}_y{countHeight}")
            with open(path + ".csv", "w+") as f:
                for i, x in enumerate(self.waveNumber()):
                    spectrum = self.spectrum(countWidth, countHeight)
                    f.write(f"{x},{spectrum[i]}\n")
                f.close()

    def saveSpectraWithoutBackground(self, path, fileName, alreadyWaveNumber=False):
        """Save the background or one specific spectrum.
        Args:
            alreadyWaveNumber(bool): 
        Return:
            CSVFile(.csv): Save the file in RawData at the folder path.
        """
        if type(alreadyWaveNumber) is not bool:
            raise TypeError("alreadyWaveNumber argument is not a boolean.")
        matrix = self.spectraWithoutBackground()
        newPath = path + "/" + "UnrawData"
        os.makedirs(newPath, exist_ok=True)
        for i in matrix:
            if fileName == "":
                fileName = "spectrum"
            x = i.x
            y = i.y
            spectrum = i.spectrum
            path = os.path.join(newPath, f"{fileName}_withoutBackground_x{x}_y{y}")
            with open(path + ".csv", "w+") as f:
                if alreadyWaveNumber == True:
                    for ind, x in enumerate(self.wavelength):
                        f.write(f"{x},{spectrum[ind]}\n")
                else:
                    for ind, x in enumerate(self.waveNumber()):
                        f.write(f"{x},{spectrum[ind]}\n")
                f.close()

    # Non-Publics functions

    def spectraWithoutBackground(self):
        """Return the data without the background.
        Return:
            dataWithoutBg(list): Contains DataPoint nameTuple. It's a copy of self.spectralPoints, but without the background.
        """
        dataWithoutBg = []
        for item in self.spectralPoints:
            x = item.x
            y = item.y
            spectrum = np.array(item.spectrum) - np.array(self.background)
            dataWithoutBg.append(DataPoint(x, y, spectrum))
        return dataWithoutBg

    def width(self):
        """Return the width (max x-axis value + 1) in the data.
        Return:
            width(int): Use in the creation of a matrix.
        """
        width = -1
        for item in self.spectralPoints:
            if item.x > width:
                width = item.x

        return width + 1

    def height(self):
        """Return the height (max -axis value + 1) in the data.
        Return:
            height(int): Use in the creation of a matrix.
        """
        height = -1
        for item in self.spectralPoints:
            if item.y > height:
                height = item.y

        return height + 1

    def spectrumLen(self):
        """Return the max len of all spectra in the data.
        Return:
            spectrumLen(int): Use in the creation of a matrix.
            None(nonetype): If spectrumLen = 0.
        """
        spectrumLen = 0
        for item in self.spectralPoints:
            if len(item.spectrum) > spectrumLen:
                spectrumLen = len(item.spectrum)
        if spectrumLen == 0:
            return None
        else:
            return spectrumLen

    def spectrumRange(self):
        """Return the max range of all spectra in the data.
        Return:
            spectrumRange(int): If spectrumRange is needed.
            None(nonetype): If self.spectralPoints is empty.
        """
        try:
            spectrumRange = round(abs(max(self.wavelength) - min(self.wavelength)))
            return spectrumRange
        except:
            return None

    def matrixData(self, width=None, height=None, subtractBackground=False):
        """Return the data in matrix format.
        Args:
            [Optional]width(int): If None it's automatic.
            [Optional]height(int): If None it's automatic.
            [Optional]subtractBackground(bool): Use the data without background if True.
        Return:
            matrixData(numpy.ndarray): Use in the creation of matrixRGB.
            None(nonetype): If any problem.
        """
        if type(width) is not int:
            if width != None:
                raise TypeError("width argument is not int.")
        if type(height) is not int:
            if height != None:
                raise TypeError("height argument is not int.")
        if type(subtractBackground) is not bool:
            raise TypeError("subtractBackground argument is not a boolean.")

        try:
            if width == None or height ==None:
                width = self.width()
                height = self.height()
            else:
                pass
            spectrumLen = self.spectrumLen()
            matrixData = np.zeros((height, width, spectrumLen))

            if subtractBackground:
                data = self.spectraWithoutBackground()
                for item in data:
                    matrixData[item.y, item.x, :] = np.array(item.spectrum)
            else:
                for item in self.spectralPoints:
                    matrixData[item.y, item.x, :] = np.array(item.spectrum)

            return matrixData
        except:
            None
