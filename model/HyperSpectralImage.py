from tkinter.filedialog import askopenfile
import matplotlib.pyplot as mpl
from typing import NamedTuple
import pandas as pd
import numpy as np
import fnmatch
import copy
import os
import re

class Pixel(NamedTuple):
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

    def dataWithoutBackground(self):
        dataWithoutBackground = []
        for item in self.data:
            x = item.x
            y = item.y
            spectrum = item.spectrum - self.background
            dataWithoutBackground.append(Pixel(x, y, spectrum))
        return dataWithoutBackground

    def setFolderPath(self, folderPath):
        self.folderpath = folderPath

    def setFileName(self, fileName):
        self.fileName = fileName

    def setBackground(self, background):
        self.background = np.array(background)

    def setWavelength(self, wavelength):
        self.wavelength = np.array(wavelength)

    def deleteWavelength(self):
        self.wavelength = []

    def waveNumber(self, laser):
        waveNumber = ((1 / laser) - (1 / self.wavelength)) * 10 ** 7
        return waveNumber.round(0)

    def addSpectrum(self, x, y, spectrum):
        self.data.append(Pixel(x, y, spectrum))

    def deleteSpectra(self):
        self.data = []

    def spectrum(self, x, y, data):
        spectrum = None
        for item in data:
            if item.x == x:
                if item.y == y:
                    spectrum = np.array(item.spectrum)

        return spectrum

    def widthImage(self, data):
        width = -1
        for item in data:
            if item.x > width:
                width = item.x

        return width + 1

    def heightImage(self, data):
        height = -1
        for item in data:
            if item.y > height:
                height = item.y

        return height + 1

    def spectrumLen(self, data):
        spectrumLen = 0
        for item in data:
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

    def matrixData(self, data):
        try:
            width = self.widthImage(data)
            height = self.heightImage(data)
            spectrumLen = self.spectrumLen(data)
            matrixData = np.zeros((height, width, spectrumLen))

            for item in data:
                matrixData[item.y, item.x, :] = np.array(item.spectrum)


            return matrixData
        except:
            return None

    def matrixRGB(self, data, colorValues, globalMaximum=True):
        try:
            width = self.widthImage(data)
            height = self.heightImage(data)
            spectrumLen = self.spectrumLen(data)


            lowRed = round(colorValues[0] * spectrumLen)
            highRed = round(colorValues[1] * spectrumLen)
            lowGreen = round(colorValues[2] * spectrumLen)
            highGreen = round(colorValues[3] * spectrumLen)
            lowBlue = round(colorValues[4] * spectrumLen)
            highBlue = round(colorValues[5] * spectrumLen)


            matrixRGB = np.zeros((height, width, 3))
            matrix = self.matrixData(data)

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
            return matrixRGB
        except:
            return None

    def listNameOfFiles(directory, extension="csv") -> list:
        foundFiles = []
        for file in os.listdir(directory):
            if fnmatch.fnmatch(file, f'*.{extension}'):
                foundFiles.append(file)
        return foundFiles

    def loadData(self, path):
        DoGetWaveLength = False
        foundFiles = []
        for file in os.listdir(path):
            if fnmatch.fnmatch(file, f'*.csv'):
                foundFiles.append(file)

        sortedPaths = foundFiles
        for name in sortedPaths:
            # Find the position
            matchCoords = re.match("\\D*?(\\d+)\\D*?(\\d+)\\D*?", name)
            if matchCoords:
                posX = int(matchCoords.group(1))
                posY = int(matchCoords.group(2))

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

                    if DoGetWaveLength == False:
                        elem_str = j.replace("\n", "")
                        elem = elem_str.split(",")
                        xAxis.append(float(elem[0]))
                        self.setWavelength(xAxis)
                DoGetWaveLength = True
                self.addSpectrum(posX, posY, spectrum)
            # matchBackground = re.match(".*?(_background)\\D*", name)
            # if matchBackground:
            #     fich = open(path + '/' + name, "r")
            #     test_str = list(fich)[14:]
            #     fich.close()
            #     xAxis = []
            #     for j in test_str:
            #         elem_str = j.replace("\n", "")
            #         elem = elem_str.split(",")
            #         xAxis.append(float(elem[1]))
            #         self.setWavelength(xAxis)

    # Save
    def saveCaptureCSV(self, data=None, countHeight=None, countWidth=None):
        if data is None:
            pass
        else:
            if self.fileName == "":
                self.fileName = "spectrum"

            newPath = self.folderPath + "/" + "RawData"
            os.makedirs(newPath, exist_ok=True)
            if countHeight is None and countWidth is None:
                path = os.path.join(newPath, f"{self.fileName}_background")
            else:
                path = os.path.join(newPath, f"{self.fileName}_x{countWidth}_y{countHeight}")
            with open(path + ".csv", "w+") as f:
                for i, x in enumerate(self.wavelength):  # TODO maybe more wavenumber?
                    f.write(f"{x},{data[i]}\n")
                f.close()

    def save_image(self):
        path = self.folderPath + "/"
        img = self.matrixRGB.astype(np.uint8)
        if self.fileName == "":
            plt.imsave(path + "matrixRGB.png", img)
        else:
            plt.imsave(path + self.fileName + "_matrixRGB.png", img)

    def saveDataWithoutBackground(self):
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
                for ind, x in enumerate(self.wavelength):
                    f.write(f"{x},{spectrum[ind]}\n")
                f.close()
