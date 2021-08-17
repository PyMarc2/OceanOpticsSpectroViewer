from tkinter.filedialog import askopenfile
import matplotlib.pyplot as plt
from typing import NamedTuple
import pandas as pd
import numpy as np
import fnmatch
import copy
import csv
import os
import re

class DataPoint(NamedTuple):
    x: int = None
    y: int = None
    spectrum: object = None

class HyperSpectralImage:
    def __init__(self):
        self.data = []
        self.wavelength = []
        self.background = []
        self.folderPath = ""
        self.fileName = ""
        self.laser = None
        self.data


    def addSpectrum(self, x, y, spectrum):
        """Add a spectrum to the data.
        Args:
            x(int): Position on the x-axis.
            y(int): Position on the y-axis.
            spectrum(list or numpy.ndarray): Spectrum to add to data.
        """
        self.data.append(DataPoint(x, y, spectrum))

    def deleteSpectra(self):
        """Delete all spectra."""
        self.data = []

    def spectrum(self, x, y, subtractBackground=False):
        """Return a specific spectrum.
        Args:
            x(int): Position on the x-axis.
            y(int): Position on the y-axis.
            subtractBackground(bool): Return the spectrum without background.
        Returns:
            spectrum(numpy.ndarray): Spectrum at the specific coordinates.
        """
        spectrum = None
        if subtractBackground:
            data = self.dataWithoutBackground()
            for item in data:
                if item.x == x:
                    if item.y == y:
                        spectrum = np.array(item.spectrum)
        else:
            for item in self.data:
                if item.x == x:
                    if item.y == y:
                        spectrum = np.array(item.spectrum)
        return spectrum


    def setBackground(self, background):
        """Set the background to data.
        Args:
            background(list or numpy.ndarray): The background.
        """
        self.background = np.array(background)

    def deleteBackground(self):
        """Delete the background."""
        self.background = []

    def setWavelength(self, wavelength):
        """Set the wavelength to data.
        Args:
            wavelength(list or numpy.ndarray): The wavelength.
        """
        self.wavelength = np.array(wavelength)

    def deleteWavelength(self):
        """Delete the wavelength."""
        self.wavelength = []

    def waveNumber(self, waves):
        waveNumber = ((1 / self.laser) - (1 / waves)) * 10 ** 7
        return waveNumber.round(0)







    def setLaserWavelength(self, laser):
        self.laser = laser

    def setFolderPath(self, folderPath):
        self.folderPath = folderPath

    def setFileName(self, fileName):
        self.fileName = fileName







    def dataWithoutBackground(self):
        dataWithoutBg = []
        for item in self.data:
            x = item.x
            y = item.y
            spectrum = np.array(item.spectrum) - np.array(self.background)
            dataWithoutBg.append(DataPoint(x, y, spectrum))
        return dataWithoutBg



    def widthImage(self):
        width = -1
        for item in self.data:
            if item.x > width:
                width = item.x

        return width + 1

    def heightImage(self):
        height = -1
        for item in self.data:
            if item.y > height:
                height = item.y

        return height + 1

    def spectrumLen(self):
        spectrumLen = 0
        for item in self.data:
            if len(item.spectrum) > spectrumLen:
                spectrumLen = len(item.spectrum)
        if spectrumLen == 0:
            return None
        else:
            return spectrumLen

    def spectrumRange(self, wavelength):
        try:
            return round(abs(max(wavelength) - min(wavelength)))
        except:
            return None

    def matrixData(self, width=None, height=None, subtractBackground=False):
        try:
            if width == None or height ==None:
                width = self.widthImage()
                height = self.heightImage()
            else:
                pass
            spectrumLen = self.spectrumLen()
            matrixData = np.zeros((height, width, spectrumLen))

            if subtractBackground:
                data = self.dataWithoutBackground()
                for item in data:
                    matrixData[item.y, item.x, :] = np.array(item.spectrum)
            else:
                for item in self.data:
                    matrixData[item.y, item.x, :] = np.array(item.spectrum)

            return matrixData
        except Exception as e:
            print(e)
            return None

    def matrixRGB(self, colorValues, globalMaximum=True, width=None, height=None, subtractBackground=False):
        try:
            if width == None or height ==None:
                width = self.widthImage()
                height = self.heightImage()
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

    def loadData(self, path):
        foundBackground = False
        doGetWaveLength = False
        foundFiles = []
        for file in os.listdir(path):
            if fnmatch.fnmatch(file, f'*.csv'):
                foundFiles.append(file)

        sortedPaths = foundFiles
        for name in sortedPaths:
            # Find the positions
            matchCoords = re.match("([A-Za-z_]*)_x(\\d+)_y(\\d+).*", name)
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
                self.addSpectrum(posX, posY, spectrum)

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

    # Save
    def saveCaptureCSV(self, countHeight=None, countWidth=None):
        if self.data == []:
            pass
        else:
            if self.fileName == "":
                self.fileName = "spectrum"

            newPath = self.folderPath + "/" + "RawData"
            os.makedirs(newPath, exist_ok=True)
            if countHeight is None and countWidth is None:
                path = os.path.join(newPath, f"{self.fileName}_background")
                with open(path + ".csv", "w+") as f:
                    for i, x in enumerate(self.waveNumber(self.wavelength)):
                        f.write(f"{x},{self.background[i]}\n")
                    f.close()
            else:
                path = os.path.join(newPath, f"{self.fileName}_x{countWidth}_y{countHeight}")
                with open(path + ".csv", "w+") as f:
                    for i, x in enumerate(self.waveNumber(self.wavelength)):
                        spectrum = self.spectrum(countWidth, countHeight)
                        f.write(f"{x},{spectrum[i]}\n")
                    f.close()

    def saveImage(self, matrixRGB):
        path = self.folderPath + "/"
        img = matrixRGB.astype(np.uint8)
        if self.fileName == "":
            plt.imsave(path + "matrixRGB.png", img)
        else:
            plt.imsave(path + self.fileName + "_matrixRGB.png", img)

    def saveDataWithoutBackground(self, alreadyWaveNumber=False):
        matrix = self.dataWithoutBackground()
        newPath = self.folderPath + "/" + "UnrawData"
        os.makedirs(newPath, exist_ok=True)
        for i in matrix:
            if self.fileName == "":
                self.fileName = "spectrum"
            x = i.x
            y = i.y
            spectrum = i.spectrum
            path = os.path.join(newPath, f"{self.fileName}_withoutBackground_x{x}_y{y}")
            with open(path + ".csv", "w+") as f:
                if alreadyWaveNumber == True:
                    for ind, x in enumerate(self.wavelength):
                        f.write(f"{x},{spectrum[ind]}\n")
                else:
                    for ind, x in enumerate(self.waveNumber(self.wavelength)):
                        f.write(f"{x},{spectrum[ind]}\n")
                f.close()
