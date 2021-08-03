import hardwarelibrary.communication.serialport as sepo
import hardwarelibrary.motion.sutterdevice as sutter
from tools.CircularList import RingBuffer

from gui.modules import mockSpectrometer as Mock
import seabreeze.spectrometers as sb
from model.microscopeModel import Model

import matplotlib.pyplot as plt
import numpy as np
import copy
import os


class MicroscopeControl:
    def __init__(self):
        self.acq = Model()
        self.expositionCounter = 0
        self.integrationCountAcq = 0
        self.liveAcquisitionData = []
        self.integrationTimeAcqRemainder_ms = 0
        self.changeLastExposition = 0
        self.movingIntegrationData = None
        self.positionSutter = None
        self.countSpectrum = 0
        self.countHeight = 0
        self.countWidth = 0
        self.heightId = None
        self.widthId = None
        self.saveData = None
        self.isAcquisitionDone = False

    # SETTINGS
    def resetMovingIntegrationData(self):
        self.movingIntegrationData = None

    def setExposureTime(self, time_in_ms=None, update=True):
        if time_in_ms is not None:
            expositionTime = time_in_ms

        else:
            expositionTime = self.acq.exposureTime

        self.acq.spec.integration_time_micros(expositionTime * 1000)
        if update:
            self.setIntegrationTime()

    def setIntegrationTime(self):
        try:
            if self.acq.integrationTime >= self.acq.exposureTime:
                self.integrationCountAcq = self.acq.integrationTime // self.acq.exposureTime
                self.integrationTimeAcqRemainder_ms = self.acq.integrationTime - (
                        self.integrationCountAcq * self.acq.exposureTime)

            else:
                self.integrationCountAcq = 1

        except ValueError:
            print('nope, wrong value of integration:D')

        if self.integrationTimeAcqRemainder_ms > 3:
            self.movingIntegrationData = RingBuffer(size_max=self.integrationCountAcq + 1)
            self.changeLastExposition = 1

        else:
            self.movingIntegrationData = RingBuffer(size_max=self.integrationCountAcq)
            self.changeLastExposition = 0

    # ACQUISITION
    def spectrumPixelAcquisition(self):
        self.isAcquisitionDone = False

        while not self.isAcquisitionDone:
            self.liveAcquisitionData = self.readDataLive().tolist()
            self.integrateData()
            liveData = np.mean(np.array(self.movingIntegrationData()), 0)

        return liveData

    def acquireBackground(self):
        if self.acq.folderPath == "":
            # call self.error_folder_name()
            pass

        else:
            try:
                # call self.disable_all_buttons()
                self.setExposureTime()
                background = self.spectrumPixelAcquisition()
                # self.startSave(data=self.backgroundData)
                # call self.enable_all_buttons()
                return background

            except Exception as e:
                print(f"Error in acquireBackground: {e}")

    def integrateData(self):
        self.isAcquisitionDone = False
        if self.expositionCounter < self.integrationCountAcq - 2:
            self.movingIntegrationData.append(self.liveAcquisitionData)
            self.expositionCounter += 1

        elif self.expositionCounter == self.integrationCountAcq - 2:
            self.movingIntegrationData.append(self.liveAcquisitionData)
            self.expositionCounter += 1
            if self.changeLastExposition:
                self.setExposureTime(self.integrationTimeAcqRemainder_ms, update=False)

        else:
            self.setExposureTime(update=False)
            self.movingIntegrationData.append(self.liveAcquisitionData)
            self.isAcquisitionDone = True
            self.expositionCounter = 0

    def readDataLive(self):
        return self.acq.spec.intensities()[2:]

    def connectDetection(self, index):
        self.acq.connectSpectro(index)
        return self.acq.spec.wavelengths()[2:]

    def connectStage(self, index):
        self.acq.connectStage(index)
        self.positionSutter = self.acq.stage.position()

    def stopAcq(self):
        pass
        # TODO update function
        # if self.isSweepThreadAlive:
        #     self.sweepThread.quit()
        #     self.isSweepThreadAlive = False
        #     self.countHeight = 0
        #     self.countWidth = 0
        #     self.countSpectrum = 0
        #     self.cmb_wave.setEnabled(True)
        #
        # else:
        #     print('Sampling already stopped.')

        # self.enable_all_buttons()

    # Begin loop
    def begin(self):
        if not self.isSweepThreadAlive:  # TODO change the variable and in controller or model init?
            if self.acq.folderPath == "":
                # call self.error_folder_name()
                pass
            elif self.acq.laserWavelength == "":
                # call self.error_laser_wavelength()
                pass
            else:
                if self.acq.stage is None or self.acq.spec is None:
                    self.connectDetection()
                    self.connectStage()

                self.isSweepThreadAlive = True  # TODO change variable... see earlier TODOS
                # self.pb_saveData.setEnabled(True)
                # self.pb_saveImage.setEnabled(True)
                # self.cmb_wave.setEnabled(False)
                # self.disable_all_buttons()
                # self.create_plot_rgb()
                # self.create_plot_spectrum()
                self.setExposureTime()
                # self.create_matrix_raw_data()
                # self.create_matrix_rgb()
                self.countSpectrum = 0
                self.countHeight = 0
                self.countWidth = 0
                self.sweep()

        else:
            print('Sampling already started.')

    def sweep(self):
        while self.isSweepThreadAlive:  # TODO change variable name
            if self.countSpectrum <= (self.acq.width * self.acq.height):
                self.spectrumPixelAcquisition()
                # self.matrix_raw_data_replace()
                # self.matrixRGB_replace()
                # self.update_rgb_plot()

                if self.acq.direction == "same":
                    try:
                        if self.countWidth < (self.acq.width - 1):
                            # wait for signal...
                            self.countWidth += 1
                            self.moveStage()
                        elif self.countHeight < (self.acq.height - 1) and self.countWidth == (self.acq.width - 1):
                            # wait for signal...
                            self.countWidth = 0
                            self.countHeight += 1
                            self.moveStage()
                        else:
                            self.stopAcq()

                    except Exception as e:
                        print(f'error in sweep same: {e}')
                        self.stopAcq()

                elif self.acq.direction == "other":
                    try:
                        if self.countHeight % 2 == 0:
                            if self.countWidth < (self.acq.width - 1):
                                # wait for signal...
                                self.countWidth += 1
                                self.moveStage()
                            elif self.countWidth == (self.acq.width - 1) and self.countHeight < (self.acq.height - 1):
                                # wait for signal...
                                self.countHeight += 1
                                self.moveStage()
                            else:
                                self.stopAcq()
                        elif self.countHeight % 2 == 1:
                            if self.countWidth > 0:
                                # wait for signal...
                                self.countWidth -= 1
                                self.moveStage()
                            elif self.countWidth == 0 and self.countHeight < (self.acq.height - 1):
                                # wait for signal...
                                self.countHeight += 1
                                self.moveStage()
                            else:
                                self.stopAcq()
                    except Exception as e:
                        print(f'error in sweep other: {e}')
                        self.stopAcq()

                self.countSpectrum += 1

            else:
                self.stopAcq()

    def moveStage(self):
        self.acq.stage.moveTo((self.positionSutter[0] + self.countWidth * self.acq.step * self.acq.stepMeasureUnit,
                               self.positionSutter[1] + self.countHeight * self.acq.step * self.acq.stepMeasureUnit,
                               self.positionSutter[2]))

    # Save
    def startSave(self, data=None, countHeight=None, countWidth=None):
        self.heightId = countHeight
        self.widthId = countWidth
        self.saveData = data
        self.saveCaptureCSV()

    def saveCaptureCSV(self):  # TODO generalize the save function(s)
        if self.saveData is None:
            pass
        else:
            spectrum = self.saveData
            if not self.acq.fileName:
                self.acq.fileName = "spectrum"

            fixedData = copy.deepcopy(spectrum)
            newPath = self.acq.folderPath + "/" + "RawData"
            os.makedirs(newPath, exist_ok=True)
            if self.heightId is None and self.widthId is None:
                path = os.path.join(newPath, f"{self.acq.fileName}_background")
            else:
                path = os.path.join(newPath, f"{self.acq.fileName}_x{self.widthId}_y{self.heightId}")
            with open(path + ".csv", "w+") as f:
                for i, x in enumerate(self.acq.waves):
                    f.write(f"{x},{fixedData[i]}\n")
                f.close()