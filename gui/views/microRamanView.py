from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5.Qt import QPixmap
import pyqtgraph as pg
from PyQt5.QtCore import pyqtSignal, Qt, QThreadPool, QThread
from PyQt5 import uic
import os
from gui.modules import mockSpectrometer as Mock
from tools.threadWorker import Worker
from tools.CircularList import RingBuffer
import numpy as np
import logging
import copy
import tools.sutterneeded.sutterdevice as phl
import seabreeze.spectrometers as sb

log = logging.getLogger(__name__)


microRamanViewUiPath = os.path.dirname(os.path.realpath(__file__)) + '{0}microRamanViewUi.ui'.format(os.sep)
print(microRamanViewUiPath)
Ui_microRamanView, QtBaseClass = uic.loadUiType(microRamanViewUiPath)


class MicroRamanView(QWidget, Ui_microRamanView):  # type: QWidget

    s_data_changed = pyqtSignal(dict)
    s_data_acquisition_done = pyqtSignal()

    def __init__(self, model=None):
        super(MicroRamanView, self).__init__()
        self.setupUi(self)
        self.model = model
        self.plotItem = None
        self.dataPlotItem = None
        self.initialize_buttons()

        self.threadpool = QThreadPool()
        self.isAcquisitionThreadAlive = False
        self.isSweepThreadAlive = False
        self.sweepWorker = Worker(self.sweep)
        self.sweepThread = QThread()
        self.saveWorker = Worker(self.save_capture_csv)
        self.saveThread = QThread()

        self.height = 3
        self.width = 3
        self.step = 1
        self.order = 1
        self.direction = 'other'
        self.exposureTime = 50
        self.integrationTimeAcq = 3000
        self.acqTimeRemainder_ms = 0
        self.countHeight = 0
        self.countWidth = 0
        self.countSpectrum = 0
        self.data = None
        self.connect_widgets()
        self.create_threads()

        self.stageDevice = phl.SutterDevice(portPath="debug")
        self.positionSutter = self.stageDevice.position()
        self.specDevices = sb.list_devices()
        if not self.specDevices:
            self.spec = Mock.MockSpectrometer()
        else:
            self.spec = sb.Spectrometer(self.specDevices[0])

        self.dataSep = 0
        self.countIntegrationWhile = 0
        self.integrationCountAcq = 0
        self.expositionCounter = 0
        self.integrationTimeAcqRemainder_ms = 0
        self.changeLastExposition = 0
        self.isAcquiringIntegration = False
        self.isAcquisitionDone = False
        self.isAcquiringBackground = False
        self.isBackgroundRemoved = False
        self.isEveryAcqDone = False
        self.launchIntegrationAcquisition = False
        self.temporaryIntegrationData = None
        self.movingIntegrationData = None
        self.backgroundData = None
        self.waves = None
        self.dataLen = None
        self.actualPosition = None
        self.matrixData = None
        self.matrixRGB = None
        self.dataPixel = []
        self.liveAcquisitionData = []

        self.dataLength = 2048  # TODO Will need to be generalized, now created for the mock spectrometer specifically

        self.lowRed = 0
        self.highRed = 85
        self.lowGreen = 86
        self.highGreen = 170
        self.lowBlue = 171
        self.highBlue = 255

        self.dSlider_red.set_left_thumb_value(0)
        self.dSlider_red.set_right_thumb_value(85)
        self.dSlider_green.set_left_thumb_value(86)
        self.dSlider_green.set_right_thumb_value(170)
        self.dSlider_blue.set_left_thumb_value(171)
        self.dSlider_blue.set_right_thumb_value(255)

        self.img = None

        # Saving Data
        self.folderPath = ""
        self.fileName = ""
        self.autoindexing = False

    def connect_widgets(self):
        self.sb_height.textChanged.connect(lambda: setattr(self, 'height', self.sb_height.value()))
        self.sb_width.textChanged.connect(lambda: setattr(self, 'width', self.sb_width.value()))
        self.sb_step.textChanged.connect(lambda: setattr(self, 'step', self.sb_step.value()))
        self.cmb_magnitude.currentTextChanged.connect(self.measure_unit)
        self.pb_sweepSame.clicked.connect(lambda: setattr(self, 'direction', 'same'))
        self.pb_sweepAlternate.clicked.connect(lambda: setattr(self, 'direction', 'other'))
        self.pb_reset.clicked.connect(self.stop_acq)
        self.pb_liveView.clicked.connect(self.begin)
        self.sb_acqTime.valueChanged.connect(lambda: setattr(self, 'integrationTimeAcq', self.sb_acqTime.value()))
        self.sb_acqTime.valueChanged.connect(self.set_integration_time)
        self.sb_exposure.valueChanged.connect(lambda: setattr(self, 'exposureTime', self.sb_exposure.value()))
        self.sb_exposure.valueChanged.connect(self.set_exposure_time)
        self.tb_folderPath.clicked.connect(self.select_save_folder)
        self.pb_saveData.clicked.connect(self.save_capture_csv)

        self.dSlider_red.valueChanged.connect(self.set_red_range)
        self.dSlider_green.valueChanged.connect(self.set_green_range)
        self.dSlider_blue.valueChanged.connect(self.set_blue_range)

    def connect_signals(self):
        # self.s_data_changed.connect(self.move_stage)
        self.s_data_changed.connect(lambda: setattr(self, 'isEveryAcqDone', True))
        self.s_data_changed.connect(self.startSaveThread)

    def create_threads(self, *args):
        self.sweepWorker.moveToThread(self.sweepThread)
        self.sweepThread.started.connect(self.sweepWorker.run)

        self.saveWorker.moveToThread(self.saveThread)
        self.saveThread.started.connect(self.saveWorker.run)

    def create_plot(self):
        self.graph_rgb.clear()
        self.plotItem = self.graph_rgb.addViewBox()
        self.plotItem.enableAutoRange()
        self.plotItem.invertY(True)
        self.plotItem.setAspectLocked()

    def create_matrix_data(self):
        self.matrixData = np.zeros((self.height, self.width, self.dataLength))

    def create_matrixRGB(self):
        # TODO to see the test sequence, set 3x3 matrix and un-comment following lines
        self.matrixRGB = np.zeros((self.height, self.width, 3))

        # area = np.array([255, 0, 0])
        # area1 = np.array([0, 255, 0])
        # area2 = np.array([0, 0, 255])
        # self.matrixRGB[0, 0, :] = area
        # self.matrixRGB[1, 1, :] = area1
        # self.matrixRGB[2, 2, :] = area2

    def initialize_buttons(self):
        self.pb_sweepSame.setIcons(QPixmap("./gui/misc/icons/sweep_same.png").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
                                   QPixmap("./gui/misc/icons/sweep_same_hover.png").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
                                   QPixmap("./gui/misc/icons/sweep_same_clicked.png").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
                                   QPixmap("./gui/misc/icons/sweep_same_selected.png").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.pb_sweepAlternate.setIcons(QPixmap("./gui/misc/icons/sweep_alternate.png").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
                                        QPixmap("./gui/misc/icons/sweep_alternate_hover.png").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
                                        QPixmap("./gui/misc/icons/sweep_alternate_clicked.png").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
                                        QPixmap("./gui/misc/icons/sweep_alternate_selected.png").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def disable_all_buttons(self):
        self.sb_height.setEnabled(False)
        self.sb_width.setEnabled(False)
        self.sb_step.setEnabled(False)
        self.cmb_magnitude.setEnabled(False)
        self.pb_sweepSame.setEnabled(False)
        self.pb_sweepAlternate.setEnabled(False)
        self.sb_exposure.setEnabled(False)
        self.sb_acqTime.setEnabled(False)

    def enable_all_buttons(self):
        self.sb_height.setEnabled(True)
        self.sb_width.setEnabled(True)
        self.sb_step.setEnabled(True)
        self.cmb_magnitude.setEnabled(True)
        self.pb_sweepSame.setEnabled(True)
        self.pb_sweepAlternate.setEnabled(True)
        self.sb_exposure.setEnabled(True)
        self.sb_acqTime.setEnabled(True)

    def measure_unit(self):
        if self.cmb_magnitude.currentText() == 'mm':
            self.order = 10**3

        elif self.cmb_magnitude.currentText() == 'um':
            self.order = 1

        elif self.cmb_magnitude.currentText() == 'nm':
            self.order = 10**(-3)

        else:
            print('What the hell is going on?!')

    def set_red_range(self):
        self.lowRed = self.dSlider_red.get_left_thumb_value()
        self.highRed = self.dSlider_red.get_right_thumb_value()
        self.matrixRGB_replace()
        print("lowRed:", self.lowRed)
        print("highRed:", self.highRed)

    def set_green_range(self):
        self.lowGreen = self.dSlider_green.get_left_thumb_value()
        self.highGreen = self.dSlider_green.get_right_thumb_value()
        self.matrixRGB_replace()
        print("lowGreen:", self.lowGreen)
        print("highGreen:", self.highGreen)

    def set_blue_range(self):
        self.lowBlue = self.dSlider_blue.get_left_thumb_value()
        self.highBlue = self.dSlider_blue.get_right_thumb_value()
        self.matrixRGB_replace()
        print("lowBlue:", self.lowBlue)
        print("highBlue:", self.highBlue)

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

        except ValueError as e:
            self.sb_acqTime.setStyleSheet('color: red')
    
        if self.integrationTimeAcqRemainder_ms > 3:
            self.movingIntegrationData = RingBuffer(size_max=self.integrationCountAcq + 1)
            self.changeLastExposition = 1
        else:
            self.movingIntegrationData = RingBuffer(size_max=self.integrationCountAcq)
            self.changeLastExposition = 0

    def launch_integration_acquisition(self):
        if self.launchIntegrationAcquisition and not self.isAcquiringIntegration:
            self.isAcquiringIntegration = True
            self.isAcquisitionDone = False

        elif self.isAcquiringIntegration:
            if not self.isAcquisitionDone:
                pass

            elif self.isAcquisitionDone:
                self.isAcquiringIntegration = False

    def acquire_background(self):
        if self.isAcquiringBackground:
            self.launchIntegrationAcquisition = True
            self.launch_integration_acquisition()

            if self.isAcquisitionDone:
                self.backgroundData = self.temporaryIntegrationData
                self.isBackgroundRemoved = True
                self.isAcquiringBackground = False

        if self.isBackgroundRemoved:
            self.dataPixel = self.dataPixel - self.backgroundData

    def integrate_data(self):
        self.isAcquisitionDone = False
        if self.expositionCounter < self.integrationCountAcq - 1:
            self.movingIntegrationData.append(self.liveAcquisitionData)
            self.expositionCounter += 1

        elif self.expositionCounter == self.integrationCountAcq - 1:
            self.movingIntegrationData.append(self.liveAcquisitionData)
            self.expositionCounter += 1
            if self.changeLastExposition:
                self.set_exposure_time(self.integrationTimeAcqRemainder_ms, update=False)
        else:
            self.set_exposure_time(update=False)
            self.movingIntegrationData.append(self.liveAcquisitionData)
            self.isAcquisitionDone = True
            self.expositionCounter = 0

    def read_data_live(self, *args, **kwargs):
        return self.spec.intensities()[2:]

    def spectrum_pixel_acquisition(self):
        # manage_data_flow homologue
        self.waves = self.spec.wavelengths()[2:]
        self.dataLen = len(self.waves)
        self.dataSep = (max(self.waves) - min(self.waves)) / len(self.waves)

        self.liveAcquisitionData = self.read_data_live().tolist()

        self.integrate_data()
        self.dataPixel = np.mean(np.array(self.movingIntegrationData()), 0)
        self.acquire_background()

    def matrix_data_replace(self):
        # Inserts dataPixel in the matrix, with the right indexes
        self.matrixData[self.countHeight, self.countWidth, :] = np.array(self.dataPixel)
        self.dataPixel = []
        self.s_data_changed.emit({f"{self.countSpectrum}": self.matrixData[self.countHeight][self.countWidth]})

    def matrixRGB_replace(self):
        if self.isSweepThreadAlive:
            lowRed = round((self.lowRed / 255) * self.dataLength)
            highRed = round((self.highRed / 255) * self.dataLength)
            lowGreen = round((self.lowGreen / 255) * self.dataLength)
            highGreen = round((self.highGreen / 255) * self.dataLength)
            lowBlue = round((self.lowBlue / 255) * self.dataLength)
            highBlue = round((self.highBlue / 255) * self.dataLength)

            self.matrixRGB[:, :, 0] = self.matrixData[:, :, lowRed:highRed].sum(axis=2)
            self.matrixRGB[:, :, 1] = self.matrixData[:, :, lowGreen:highGreen].sum(axis=2)
            self.matrixRGB[:, :, 2] = self.matrixData[:, :, lowBlue:highBlue].sum(axis=2)
            self.matrixRGB = (self.matrixRGB / np.max(self.matrixRGB)) * 255

        else:
            pass

    def update_plot(self):
        img = pg.ImageItem(image=self.matrixRGB, levels=(0, 1))
        self.plotItem.addItem(img)

    def move_stage(self):
        self.stageDevice.moveTo((self.positionSutter[0]+self.countWidth*self.step,
                                 self.positionSutter[1]+self.countHeight*self.step,
                                 self.positionSutter[2]))
        # TODO we will need to import the communication file/module for any Sutter device (hardwareLibrary)

    def sweep(self, *args, **kwargs):
        while self.isSweepThreadAlive:
            if self.countSpectrum < self.width*self.height:
                self.spectrum_pixel_acquisition()
                self.matrix_data_replace()
                self.matrixRGB_replace()
                self.update_plot()
                if self.direction == "same":
                    if self.countWidth < self.width-1:
                        # wait for signal... (with a connect?)
                        self.countWidth += 1
                        self.move_stage()
                    elif self.countHeight < self.height and self.countWidth == self.width-1:
                        if self.countSpectrum < self.width*self.height-1:
                            # wait for signal...
                            self.countWidth = 0
                            self.countHeight += 1
                            self.move_stage()
                        else:
                            self.isSweepThreadAlive = False
                            self.enable_all_buttons()
                    else:
                        self.isSweepThreadAlive = False
                        raise Exception(
                            'Somehow, the loop is trying to create more row or columns than asked on the GUI.')

                elif self.direction == "other":
                    if self.countWidth < self.width - 1 and self.countHeight % 2 == 0:
                        # wait for signal...
                        self.countWidth += 1
                        self.move_stage()
                    elif self.countWidth == self.width - 1 and self.countHeight % 2 == 0:
                        # wait for signal...
                        self.countHeight += 1
                        if self.countHeight == self.height:
                            self.isSweepThreadAlive = False
                        else:
                            self.move_stage()
                    elif 0 < self.countWidth < self.width and self.countHeight % 2 == 1:
                        # wait for signal...
                        self.countWidth -= 1
                        self.move_stage()
                    elif self.countWidth == 0 and self.countHeight % 2 == 1:
                        # wait for signal...
                        self.countHeight += 1
                        if self.countHeight == self.height:
                            self.isSweepThreadAlive = False
                        else:
                            pass
                            # self.move_stage()
                    else:
                        self.isSweepThreadAlive = False
                        raise Exception(
                            'Somehow, the loop is trying to create more columns or rows than asked on the GUI.')
                self.countSpectrum += 1
            else:
                self.isSweepThreadAlive = False
                self.enable_all_buttons()

    def begin(self):
        if not self.isSweepThreadAlive:
            try:
                self.isSweepThreadAlive = True
                self.set_integration_time()
                self.set_exposure_time()
                self.graph_rgb.clear()
                self.create_plot()
                self.disable_all_buttons()
                self.create_matrix_data()
                self.create_matrixRGB()
                self.sweepThread.start()
                self.threadpool.start(self.sweepWorker)

            except Exception as e:
                self.spec = Mock.MockSpectrometer()

        else:
            print('Sampling already started.')

    def stop_acq(self):
        if self.isSweepThreadAlive:
            self.sweepThread.terminate()
            self.saveThread.terminate()
            self.isSweepThreadAlive = False
        else:
            print('Sampling already stopped.')

        self.enable_all_buttons()

    def start_save_thread(self, data=None):
        self.data = data
        self.saveThread.start()

    def stop_save_thread(self):
        self.saveThread.wait()

    def select_save_folder(self):
        self.folderPath = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if self.folderPath != "":
            self.le_folderPath.setText(self.folderPath)

    def toggle_autoindexing(self):
        pass

    def save_capture_csv(self, *args, **kwargs):
        if self.data is None:
            pass
        elif self.data is not None:
            key, spectrum = self.data.items()[0]
            self.fileName = self.le_fileName.text()
            if self.fileName == "":
                self.fileName = f"spectrum_{self.direction}"

            if self.folderPath == "":
                pass

            else:
                fixedData = copy.deepcopy(spectrum)
                path = os.path.join(self.folderPath, f"{self.fileName}_{key}")
                # print(key, spectrum)
                with open(path + ".csv", "w+") as f:
                    for i, x in enumerate(self.waves):
                        f.write(f"{x},{fixedData[i]}\n")
                    f.close()

            self.stopSaveThread()
