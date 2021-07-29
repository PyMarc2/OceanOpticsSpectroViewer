import tools.sutterneeded.communication.serialport as sepo
import tools.sutterneeded.sutterdevice as sutter
from tools.CircularList import RingBuffer

from gui.modules import mockSpectrometer as Mock
import seabreeze.spectrometers as sb

import matplotlib.pyplot as plt
import numpy as np
import copy
import os


class Microscope:
    def __init__(self):
        self.waves = Mock.MockSpectrometer().wavelengths()[2:]
        self.spec = Mock.MockSpectrometer()
        self.expositionCounter = 0
        self.exposureTime = 1000
        self.integrationTimeAcq = 5000
        self.integrationCountAcq = 0
        self.movingIntegrationData = None
        self.isAcquiringBackground = False
        self.dataPixel = []
        self.liveAcquisitionData = []
        self.integrationTimeAcqRemainder_ms = 0
        self.isAcquisitionDone = False
        self.changeLastExposition = 0
        self.dataSep = 0
        self.dataLen = 0
        self.backgroundData = []
        self.matrixRawData = None

    # SETTINGS
    def set_exposure_time(self, time_in_ms=None, update=True):
        if time_in_ms is not None:
            expositionTime = time_in_ms

        else:
            expositionTime = self.exposureTime

        self.spec.integration_time_micros(expositionTime * 1000)
        if update:
            self.set_integration_time()

    def set_integration_time(self):
        try:
            if self.integrationTimeAcq >= self.exposureTime:
                self.integrationCountAcq = self.integrationTimeAcq // self.exposureTime
                self.integrationTimeAcqRemainder_ms = self.integrationTimeAcq - (
                        self.integrationCountAcq * self.exposureTime)

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
    def spectrum_pixel_acquisition(self):
        # self.set_exposure_time()
        self.isAcquisitionDone = False

        self.waves = self.spec.wavelengths()[2:]
        self.dataLen = len(self.waves)
        self.dataSep = (max(self.waves) - min(self.waves)) / len(self.waves)

        while not self.isAcquisitionDone:
            self.liveAcquisitionData = self.read_data_live().tolist()
            self.integrate_data()
            self.dataPixel = np.mean(np.array(self.movingIntegrationData()), 0)

        return self.dataPixel

    def acquire_background(self):
        if self.folderPath == "":
            self.error_folder_name()

        else:
            try:
                self.disable_all_buttons()
                self.set_exposure_time()
                self.isAcquiringBackground = True
                self.spectrum_pixel_acquisition()
                self.backgroundData = self.dataPixel
                self.start_save(data=self.backgroundData)
                self.enable_all_buttons()

            except Exception as e:
                print(f"Error in acquire_background: {e}")

        self.isAcquiringBackground = False

    def integrate_data(self):
        self.isAcquisitionDone = False
        if self.expositionCounter < self.integrationCountAcq - 2:
            self.movingIntegrationData.append(self.liveAcquisitionData)
            self.expositionCounter += 1

        elif self.expositionCounter == self.integrationCountAcq - 2:
            self.movingIntegrationData.append(self.liveAcquisitionData)
            self.expositionCounter += 1
            if self.changeLastExposition:
                self.set_exposure_time(self.integrationTimeAcqRemainder_ms, update=False)

        else:
            self.set_exposure_time(update=False)
            self.movingIntegrationData.append(self.liveAcquisitionData)
            self.isAcquisitionDone = True
            self.expositionCounter = 0

    def read_data_live(self):
        return self.spec.intensities()[2:]

    def connect_detection(self):
        pass

    def connect_stage(self):
        pass

    def create_matrix_raw_data(self):
        self.matrixRawData = np.zeros((self.height, self.width, self.dataLen))

    def stop_acq(self):  # TODO here?
        if self.isSweepThreadAlive:
            self.sweepThread.quit()
            self.isSweepThreadAlive = False
            self.countHeight = 0
            self.countWidth = 0
            self.countSpectrum = 0
            self.cmb_wave.setEnabled(True)

        else:
            print('Sampling already stopped.')

        # self.enable_all_buttons()

    def matrix_raw_data_replace(self):
        self.matrixRawData[self.countHeight, self.countWidth, :] = np.array(self.dataPixel)
        self.dataPixel = []
        # self.start_save(self.matrixRawData[self.countHeight, self.countWidth, :], self.countHeight, self.countWidth)

    # Begin loop
    def begin(self):  # TODO here?
        if not self.isSweepThreadAlive:
            if self.folderPath == "":
                self.error_folder_name()
            elif self.le_laser.text() == "":
                self.error_laser_wavelength()
            else:
                if self.stageDevice is None or self.spec is None:
                    self.connect_detection()
                    self.connect_stage()

                self.isSweepThreadAlive = True
                self.pb_saveData.setEnabled(True)
                self.pb_saveImage.setEnabled(True)
                self.cmb_wave.setEnabled(False)
                self.disable_all_buttons()
                self.create_plot_rgb()
                self.create_plot_spectrum()
                self.set_exposure_time()
                self.create_matrix_raw_data()
                self.create_matrix_rgb()
                self.sweepThread.start()

        else:
            print('Sampling already started.')

    def move_stage(self):
        self.stageDevice.moveTo((self.positionSutter[0] + self.countWidth * self.step * self.order,
                                 self.positionSutter[1] + self.countHeight * self.step * self.order,
                                 self.positionSutter[2]))

    # Save
    def start_save(self, data=None, countHeight=None, countWidth=None):
        self.heightId = countHeight
        self.widthId = countWidth
        self.data = data
        self.save_capture_csv()

    def select_save_folder(self):
        self.folderPath = self.directory  # str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if self.folderPath != "":
            self.le_folderPath.setText(self.folderPath)

    def save_capture_csv(self):
        if self.data is None:
            pass
        else:
            spectrum = self.data
            self.fileName = self.le_fileName.text()
            if self.fileName == "":
                self.fileName = "spectrum"

            fixedData = copy.deepcopy(spectrum)
            newPath = self.folderPath + "/" + "RawData"
            os.makedirs(newPath, exist_ok=True)
            if self.heightId is None and self.widthId is None:
                path = os.path.join(newPath, f"{self.fileName}_background")
            else:
                path = os.path.join(newPath, f"{self.fileName}_x{self.widthId}_y{self.heightId}")
            with open(path + ".csv", "w+") as f:
                for i, x in enumerate(self.waves):
                    f.write(f"{x},{fixedData[i]}\n")
                f.close()

    def save_data_without_background(self, *args, **kwargs):
        matrix = self.matrixDataWithoutBackground
        newPath = self.folderPath + "/" + "UnrawData"
        os.makedirs(newPath, exist_ok=True)
        for i in range(self.height):
            for j in range(self.width):
                spectrum = matrix[i, j, :]
                self.fileName = self.le_fileName.text()
                if self.fileName == "":
                    self.fileName = "spectrum"
                path = os.path.join(newPath, f"{self.fileName}_withoutBackground_x{i}_y{j}")
                with open(path + ".csv", "w+") as f:
                    for ind, x in enumerate(self.waves):
                        f.write(f"{x},{spectrum[ind]}\n")
                    f.close()

        path = newPath + "/"
        if self.fileName == "":
            file = "matrixDataWithoutBackground.csv"
        else:
            file = self.fileName + "_matrixDataWithoutBackground.csv"

        with open(path + file, "w+") as f:
            f.write("[")
            for i, x in enumerate(matrix):
                if i == 0:
                    f.write("[")
                else:
                    f.write("\n\n[")
                for ii, y in enumerate(x):
                    if ii == 0:
                        f.write("[")
                    else:
                        f.write("\n[")
                    for iii, z, in enumerate(y):
                        if iii != len(y) - 1:
                            f.write(f"{z}, ")
                        else:
                            f.write(f"{z}")
                    f.write("]")
                f.write("]")
            f.write("]")

            f.close()
