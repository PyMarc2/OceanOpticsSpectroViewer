from PyQt5.QtCore import pyqtSignal, Qt, QThreadPool, QThread, QTimer
from PyQt5.QtWidgets import QWidget, QFileDialog
from PyQt5.Qt import QPixmap
from PyQt5 import uic

import tools.sutterneeded.communication.serialport as sepo
import tools.sutterneeded.sutterdevice as sutter
from tools.CircularList import RingBuffer
from tools.threadWorker import Worker

from gui.modules import mockSpectrometer as Mock
import seabreeze.spectrometers as sb

import pyqtgraph as pg
import numpy as np
import logging
import copy
import os

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

        self.direction = "other"
        self.folderPath = ""
        self.fileName = ""

        self.liveAcquisitionData = []
        self.dataPixel = []

        self.saveWorker = Worker(self.save_capture_csv)
        self.sweepWorker = Worker(self.sweep)


        self.integrationTimeAcqRemainder_ms = 0
        self.integrationTimeAcq = 3000
        self.countIntegrationWhile = 0
        self.changeLastExposition = 0
        self.acqTimeRemainder_ms = 0
        self.integrationCountAcq = 0
        self.expositionCounter = 0
        self.countSpectrum = 0
        self.order = 10 ** 3
        self.countHeight = 0
        self.countWidth = 0
        self.dataSep = 0

        self.doSliderPositionAreInitialize = False
        self.launchIntegrationAcquisition = False
        self.isAcquisitionThreadAlive = False
        self.isAcquiringIntegration = False
        self.isAcquiringBackground = False
        self.isBackgroundRemoved = False
        self.isSweepThreadAlive = False
        self.detectionConnected = False
        self.isAcquisitionDone = False
        self.isEveryAcqDone = False
        self.lightConnected = False
        self.stageConnected = False
        self.autoindexing = False

        self.colorRangeViewEnable = True

        self.temporaryIntegrationData = None
        self.movingIntegrationData = None
        self.backgroundData = None
        self.actualPosition = None
        self.mousePositionX = None
        self.mousePositionY = None
        self.positionSutter = None
        self.plotSpectrum = None
        self.stageDevice = None
        self.plotViewBox = None
        self.matrixData = None
        self.greenRange = None
        self.blueRange = None
        self.matrixRGB = None
        self.countSave = None
        self.plotItem = None
        self.redRange = None
        self.heightId = None
        self.widthId = None
        self.dataLen = None
        self.Height = None
        self.Width = None
        self.waves = None
        self.spec = None
        self.data = None
        self.img = None

        self.height = self.sb_height.value()
        self.width = self.sb_width.value()
        self.step = self.sb_step.value()
        self.threadpool = QThreadPool()
        self.sweepThread = QThread()
        self.update_slider_status()
        self.saveThread = QThread()
        self.initialize_buttons()
        self.connect_widgets()
        self.create_threads()

        self.lightDevices = ["None"]
        self.stageDevices = sepo.SerialPort.matchPorts(idVendor=4930, idProduct=1)
        self.stageDevices.insert(0, "Debug")
        self.listStageDevices = []
        for el in self.stageDevices:
            self.listStageDevices.append(str(el))
        self.specDevices = sb.list_devices()
        self.specDevices.insert(0, "MockSpectrometer")
        self.listSpecDevices = []
        for el in self.specDevices:
            self.listSpecDevices.append(str(el))
        self.cmb_selectDetection.addItems(self.listSpecDevices)
        self.cmb_selectLight.addItems(self.lightDevices)
        self.cmb_selectStage.addItems(self.listStageDevices)



    # Connect
    def connect_widgets(self):
        self.cmb_magnitude.currentTextChanged.connect(self.set_measure_unit)
        self.dSlider_red.valueChanged.connect(self.set_red_range)
        self.dSlider_green.valueChanged.connect(self.set_green_range)
        self.dSlider_blue.valueChanged.connect(self.set_blue_range)
        self.graph_rgb.scene().sigMouseMoved.connect(self.mouse_moved)
        self.pb_saveData.clicked.connect(self.save_capture_csv)
        self.pb_sweepSame.clicked.connect(lambda: setattr(self, 'direction', 'same'))
        self.pb_sweepAlternate.clicked.connect(lambda: setattr(self, 'direction', 'other'))
        self.pb_reset.clicked.connect(self.stop_acq)
        self.pb_liveView.clicked.connect(self.begin)
        self.pb_connectLight.clicked.connect(self.connect_light)
        self.pb_connectStage.clicked.connect(self.connect_stage)
        self.pb_connectDetection.clicked.connect(self.connect_detection)
        self.sb_height.textChanged.connect(lambda: setattr(self, 'height', self.sb_height.value()))
        self.sb_width.textChanged.connect(lambda: setattr(self, 'width', self.sb_width.value()))
        self.sb_step.textChanged.connect(lambda: setattr(self, 'step', self.sb_step.value()))
        self.sb_acqTime.valueChanged.connect(lambda: setattr(self, 'integrationTimeAcq', self.sb_acqTime.value()))
        self.sb_acqTime.valueChanged.connect(self.set_integration_time)
        self.sb_exposure.valueChanged.connect(lambda: setattr(self, 'exposureTime', self.sb_exposure.value()))
        self.sb_exposure.valueChanged.connect(self.set_exposure_time)
        self.tb_folderPath.clicked.connect(self.select_save_folder)

        self.sb_highRed.valueChanged.connect(self.update_slider_status)
        self.sb_lowRed.valueChanged.connect(self.update_slider_status)
        self.sb_highGreen.valueChanged.connect(self.update_slider_status)
        self.sb_lowGreen.valueChanged.connect(self.update_slider_status)
        self.sb_highBlue.valueChanged.connect(self.update_slider_status)
        self.sb_lowBlue.valueChanged.connect(self.update_slider_status)


        self.cb_colorRangeView.stateChanged.connect(self.colorRangeView_status)

    def connect_light(self):  # Connect the light
        log.debug("Initializing devices...")
        index = self.cmb_selectLight.currentIndex()
        if index == 0:
            # self.spec = Mock.MockSpectrometer()
            log.info("No light connected")
            self.lightConnected = False
        else:
            self.lightConnected = True

    def connect_stage(self):  # Connect the light
        log.debug("Initializing devices...")
        self.stageDevice = sutter.SutterDevice()
        self.stageDevice.doInitializeDevice()
        if self.stageDevice is None:
            raise Exception('The sutter is not connected!')
        # index = self.cmb_selectStage.currentIndex()
        # if index == 0:
            # log.info("No stage connected; FakeStage Enabled.")
            # self.stageDevice = phl.SutterDevice(portPath="debug")
            # self.stageConnected = True
        # else:
            # self.stageDevice = None
            # self.stageConnected = True
        self.positionSutter = self.stageDevice.position()
        # print(self.positionSutter)

    def connect_detection(self):  # Connect the light
        log.debug("Initializing devices...")
        index = self.cmb_selectDetection.currentIndex()
        if index == 0:
            self.spec = Mock.MockSpectrometer()
            log.info("No device connected; Mocking Spectrometer Enabled.")
            self.detectionConnected = True
        else:
            self.spec = sb.Spectrometer(self.specDevices[index])
            log.info("Devices:{}".format(self.specDevices))
            self.detectionConnected = True
        self.set_exposure_time()

    def mouse_moved(self, pos):
        try:
            value = self.plotViewBox.mapSceneToView(pos)
            valueSTR = str(value)
            valueMin = valueSTR.find("(")
            valueMax = valueSTR.find(")")
            position = valueSTR[valueMin+1:valueMax]
            position = position.split(",")
            positionX = int(float(position[0]))
            positionY = int(float(position[1]))

            if positionX <= -1 or positionY <= -1:
                pass

            else:
                self.mousePositionX = positionX
                self.mousePositionY = positionY
                self.update_spectrum_plot()
        except Exception:
            pass

    def error_folder_name(self):
        self.le_folderPath.setStyleSheet("background-color: rgb(255, 0, 0)")
        QTimer.singleShot(50, lambda: self.le_folderPath.setStyleSheet("background-color: rgb(255,255,255)"))

    # Create
    def create_threads(self):
        self.sweepWorker.moveToThread(self.sweepThread)
        self.sweepThread.started.connect(self.sweepWorker.run)

        # self.saveWorker.moveToThread(self.saveThread)
        # self.saveThread.started.connect(self.saveWorker.run)

    def create_matrix_data(self):
        self.matrixData = np.zeros((self.height, self.width, self.dataLen))

    def create_matrix_rgb(self):
        self.matrixRGB = np.zeros((self.height, self.width, 3))

    def create_plot_rgb(self):
        self.graph_rgb.clear()
        self.plotViewBox = self.graph_rgb.addViewBox()
        self.plotViewBox.enableAutoRange()
        self.plotViewBox.invertY(True)
        self.plotViewBox.setAspectLocked()

    def create_plot_spectrum(self):
        self.graph_spectre.clear()
        self.plotItem = self.graph_spectre.addPlot()
        self.plotSpectrum = self.plotItem.plot()
        self.plotRedRange = self.plotItem.plot()
        self.plotGreenRange = self.plotItem.plot()
        self.plotBlueRange = self.plotItem.plot()
        self.plotBlack = self.plotItem.plot()
        self.plotItem.enableAutoRange()

    # Buttons
    def initialize_buttons(self):
        self.pb_sweepSame.setIcons(QPixmap("./gui/misc/icons/sweep_same.png").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
                                   QPixmap("./gui/misc/icons/sweep_same_hover.png").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
                                   QPixmap("./gui/misc/icons/sweep_same_clicked.png").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
                                   QPixmap("./gui/misc/icons/sweep_same_selected.png").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.pb_sweepAlternate.setIcons(QPixmap("./gui/misc/icons/sweep_alternate.png").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
                                        QPixmap("./gui/misc/icons/sweep_alternate_hover.png").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
                                        QPixmap("./gui/misc/icons/sweep_alternate_clicked.png").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation),
                                        QPixmap("./gui/misc/icons/sweep_alternate_selected.png").scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def enable_all_buttons(self):
        self.cmb_selectDetection.setEnabled(True)
        self.cmb_selectLight.setEnabled(True)
        self.cmb_selectStage.setEnabled(True)
        self.cmb_magnitude.setEnabled(True)
        self.pb_connectDetection.setEnabled(True)
        self.pb_sweepAlternate.setEnabled(True)
        self.pb_connectLight.setEnabled(True)
        self.pb_connectStage.setEnabled(True)
        self.pb_sweepSame.setEnabled(True)
        self.sb_exposure.setEnabled(True)
        self.sb_acqTime.setEnabled(True)
        self.sb_height.setEnabled(True)
        self.sb_width.setEnabled(True)
        self.sb_step.setEnabled(True)

    def disable_all_buttons(self):
        self.cmb_selectDetection.setEnabled(False)
        self.cmb_selectLight.setEnabled(False)
        self.cmb_selectStage.setEnabled(False)
        self.cmb_magnitude.setEnabled(False)
        self.pb_connectDetection.setEnabled(False)
        self.pb_sweepAlternate.setEnabled(False)
        self.pb_connectLight.setEnabled(False)
        self.pb_connectStage.setEnabled(False)
        self.pb_sweepSame.setEnabled(False)
        self.sb_exposure.setEnabled(False)
        self.sb_acqTime.setEnabled(False)
        self.sb_height.setEnabled(False)
        self.sb_width.setEnabled(False)
        self.sb_step.setEnabled(False)

    # Set
    def set_red_range(self):
        self.sb_lowRed.setValue(self.dSlider_red.get_left_thumb_value())
        self.sb_highRed.setValue(self.dSlider_red.get_right_thumb_value())
        try:
            self.matrixRGB_replace()
            self.update_rgb_plot()
            self.update_spectrum_plot()
        except:
            pass

    def set_green_range(self):
        self.sb_lowGreen.setValue(self.dSlider_green.get_left_thumb_value())
        self.sb_highGreen.setValue(self.dSlider_green.get_right_thumb_value())
        try:
            self.matrixRGB_replace()
            self.update_rgb_plot()
            self.update_spectrum_plot()
        except:
            pass

    def set_blue_range(self):
        self.sb_lowBlue.setValue(self.dSlider_blue.get_left_thumb_value())
        self.sb_highBlue.setValue(self.dSlider_blue.get_right_thumb_value())
        try:
            self.matrixRGB_replace()
            self.update_rgb_plot()
            self.update_spectrum_plot()
        except:
            pass

    def set_measure_unit(self):
        if self.cmb_magnitude.currentText() == 'mm':
            self.order = 10**3

        elif self.cmb_magnitude.currentText() == 'um':
            self.order = 1

        elif self.cmb_magnitude.currentText() == 'nm':
            self.order = 10**(-3)

        else:
            print('What the hell is going on?!')

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
            self.sb_acqTime.setStyleSheet('color: red')

        if self.integrationTimeAcqRemainder_ms > 3:
            self.movingIntegrationData = RingBuffer(size_max=self.integrationCountAcq + 1)
            self.changeLastExposition = 1

        else:
            self.movingIntegrationData = RingBuffer(size_max=self.integrationCountAcq)
            self.changeLastExposition = 0

    # Acquisition
    def launch_integration_acquisition(self):
        if self.launchIntegrationAcquisition and not self.isAcquiringIntegration:
            self.isAcquiringIntegration = True
            self.isAcquisitionDone = False

        elif self.isAcquiringIntegration:
            if not self.isAcquisitionDone:
                pass

            elif self.isAcquisitionDone:
                self.isAcquiringIntegration = False

    def spectrum_pixel_acquisition(self):
        self.waves = self.spec.wavelengths()[2:]
        self.dataLen = len(self.waves)
        self.dataSep = (max(self.waves) - min(self.waves)) / len(self.waves)

        self.liveAcquisitionData = self.read_data_live().tolist()

        self.integrate_data()

        if not self.isAcquiringBackground:
            self.dataPixel = np.mean(np.array(self.movingIntegrationData()), 0)
        else:
            self.backgroundData = np.mean(np.array(self.movingIntegrationData()), 0)

    def acquire_background(self):
        self.isAcquiringBackground = True
        if self.folderPath == "":
            self.error_folder_name()

        if self.stageDevice is None or self.spec is None:
            self.connect_detection()
            self.connect_stage()

        try:
            self.disable_all_buttons()
            self.set_integration_time()
            self.spectrum_pixel_acquisition()
            self.start_save_thread(data=self.backgroundData)
            self.enable_all_buttons()

        except Exception as e:
            print(f"Error in acquire_background: {e}")

        self.isAcquiringBackground = False

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

    def read_data_live(self):
        return self.spec.intensities()[2:]

    def stop_acq(self):
        if self.isSweepThreadAlive:
            self.sweepThread.terminate()
            # self.saveThread.terminate()
            self.isSweepThreadAlive = False
            self.countHeight = 0
            self.countWidth = 0
            self.countSpectrum = 0
            self.stageDevice = None
            self.spec = None

        else:
            print('Sampling already stopped.')

        self.enable_all_buttons()

    # Update
    def update_rgb_plot(self):
        #matrix = self.matrixRGB.transpose()
        vb = pg.ImageItem(image=self.matrixRGB)
        self.plotViewBox.addItem(vb)

    def update_spectrum_plot(self):
        try:
            maximum = max(self.matrixData[self.mousePositionY, self.mousePositionX, :])
            minimum = min(self.matrixData[self.mousePositionY, self.mousePositionX, :]) - 1
        except Exception:
            maximum = 1
            minimum = 0

        if self.colorRangeViewEnable:
            lowRed = round((self.sb_lowRed.value() / 255) * (len(self.waves) - 1))
            highRed = round((self.sb_highRed.value() / 255) * (len(self.waves) - 1))
            lowGreen = round((self.sb_lowGreen.value() / 255) * (len(self.waves) - 1))
            highGreen = round((self.sb_highGreen.value() / 255) * (len(self.waves) - 1))
            lowBlue = round((self.sb_lowBlue.value() / 255) * (len(self.waves) - 1))
            highBlue = round((self.sb_highBlue.value() / 255) * (len(self.waves) - 1))

            self.redRange = np.full(len(self.waves), minimum)
            self.redRange[lowRed] = maximum
            self.redRange[highRed] = maximum

            self.greenRange = np.full(len(self.waves), minimum)
            self.greenRange[lowGreen] = maximum
            self.greenRange[highGreen] = maximum

            self.blueRange = np.full(len(self.waves), minimum)
            self.blueRange[lowBlue] = maximum
            self.blueRange[highBlue] = maximum

            self.plotRedRange.setData(self.waves, self.redRange, pen=(255, 0, 0))
            self.plotGreenRange.setData(self.waves, self.greenRange, pen=(0, 255, 0))
            self.plotBlueRange.setData(self.waves, self.blueRange, pen=(0, 0, 255))
            self.plotBlack.setData(self.waves, np.full(len(self.waves), minimum), pen=(0, 0, 0))

        if not self.colorRangeViewEnable:
            self.plotRedRange.setData(self.waves, np.full(len(self.waves), minimum), pen=(0, 0, 0))
            self.plotGreenRange.setData(self.waves, np.full(len(self.waves), minimum), pen=(0, 0, 0))
            self.plotBlueRange.setData(self.waves, np.full(len(self.waves), minimum), pen=(0, 0, 0))
            self.plotBlack.setData(self.waves, np.full(len(self.waves), minimum), pen=(0, 0, 0))

        self.plotSpectrum.setData(self.waves, self.matrixData[self.mousePositionY, self.mousePositionX, :])

    def matrix_data_replace(self):
        self.matrixData[self.countHeight, self.countWidth, :] = np.array(self.dataPixel)
        self.dataPixel = []
        self.start_save_thread(self.matrixData[self.countHeight, self.countWidth, :], self.countHeight, self.countWidth)

    def matrixRGB_replace(self):
        lowRed = round((self.sb_lowRed.value() / 255) * (len(self.waves)-1))
        highRed = round((self.sb_highRed.value() / 255) * (len(self.waves)-1))+1
        lowGreen = round((self.sb_lowGreen.value() / 255) * (len(self.waves)-1))
        highGreen = round((self.sb_highGreen.value() / 255) * (len(self.waves)-1))+1
        lowBlue = round((self.sb_lowBlue.value() / 255) * (len(self.waves)-1))
        highBlue = round((self.sb_highBlue.value() / 255) * (len(self.waves)-1))+1

        self.matrixRGB[:, :, 0] = self.matrixData[:, :, lowRed:highRed].sum(axis=2)
        self.matrixRGB[:, :, 1] = self.matrixData[:, :, lowGreen:highGreen].sum(axis=2)
        self.matrixRGB[:, :, 2] = self.matrixData[:, :, lowBlue:highBlue].sum(axis=2)

        self.matrixRGB = (self.matrixRGB / np.max(self.matrixRGB)) * 255
        self.matrixRGB = self.matrixRGB.round(0)
        # self.matrixRGB.transpose()

    def update_slider_status(self):
        self.dSlider_red.set_left_thumb_value(self.sb_lowRed.value())
        self.dSlider_red.set_right_thumb_value(self.sb_highRed.value())
        self.dSlider_green.set_left_thumb_value(self.sb_lowGreen.value())
        self.dSlider_green.set_right_thumb_value(self.sb_highGreen.value())
        self.dSlider_blue.set_left_thumb_value(self.sb_lowBlue.value())
        self.dSlider_blue.set_right_thumb_value(self.sb_highBlue.value())

        if self.doSliderPositionAreInitialize:
            try:
                self.update_spectrum_plot()
            except:
                pass
        else:
            self.doSliderPositionAreInitialize = True


    def colorRangeView_status(self):
        if self.cb_colorRangeView.checkState() == 2:
            self.colorRangeViewEnable = True
        if self.cb_colorRangeView.checkState() == 0:
            self.colorRangeViewEnable = False
        try:
            self.update_spectrum_plot()
        except:
            pass

    # Begin loop
    def begin(self):
        if not self.isSweepThreadAlive:
            if self.folderPath == "":
                self.error_folder_name()
            else:
                try:
                    if self.stageDevice is None or self.spec is None:
                        self.connect_detection()
                        self.connect_stage()

                    self.isSweepThreadAlive = True
                    self.set_integration_time()
                    self.create_plot_rgb()
                    self.create_plot_spectrum()
                    self.disable_all_buttons()
                    self.spectrum_pixel_acquisition()
                    self.create_matrix_data()
                    self.create_matrix_rgb()
                    self.sweepThread.start()

                except Exception as e:
                    print(f"Error in begin: {e}")

        else:
            print('Sampling already started.')

    def sweep(self, *args, **kwargs):
        # TODO correct the last index in height which seems to go higher than asked for
        while self.isSweepThreadAlive:
            if self.countSpectrum < (self.width*self.height):
                if self.countHeight != 0 or self.countWidth != 0:
                    self.spectrum_pixel_acquisition()
                self.matrix_data_replace()
                self.matrixRGB_replace()
                self.update_rgb_plot()

                if self.direction == "same":
                    try:
                        if self.countWidth < (self.width-1):
                            # wait for signal... (with a connect?)
                            self.countWidth += 1
                            self.move_stage()
                        elif self.countHeight < (self.height-1) and self.countWidth == (self.width-1):
                            # wait for signal...
                            self.countWidth = 0
                            self.countHeight += 1
                            self.move_stage()
                        else:
                            self.stop_acq()

                    except Exception as e:
                        print(f'error in sweep same: {e}')
                        self.stop_acq()

                elif self.direction == "other":
                    if self.countSpectrum < (self.width*self.height - 1):
                        try:
                            if self.countHeight % 2 == 0:
                                if self.countWidth < (self.width-1):
                                    # wait for signal...
                                    self.countWidth += 1
                                    self.move_stage()
                                elif self.countWidth == (self.width-1) and self.countHeight < (self.height-1):
                                    # wait for signal...
                                    self.countHeight += 1
                                    self.move_stage()
                                else:
                                    self.stop_acq()
                            elif self.countHeight % 2 == 1:
                                if self.countWidth > 0:
                                    # wait for signal...
                                    self.countWidth -= 1
                                    self.move_stage()
                                elif self.countWidth == 0 and self.countHeight < (self.height-1):
                                    # wait for signal...
                                    self.countHeight += 1
                                    self.move_stage()
                                else:
                                    self.stop_acq()
                        except Exception as e:
                            print(f'error in sweep other: {e}')
                            self.stop_acq()
                    else:
                        self.stop_acq()

                self.countSpectrum += 1

            else:
                self.stop_acq()

    def move_stage(self):
        self.stageDevice.moveTo((self.positionSutter[0]+self.countWidth*self.step*self.order,
                                 self.positionSutter[1]+self.countHeight*self.step*self.order,
                                 self.positionSutter[2]))

    # Save
    def start_save_thread(self, data=None, countHeight=None, countWidth=None):
        self.heightId = countHeight
        self.widthId = countWidth
        self.data = data
        # self.sweepThread.wait()
        # self.saveThread.start()
        self.save_capture_csv()

    def stop_save_thread(self):
        self.saveThread.wait()
        self.sweepThread.start()

    def select_save_folder(self):
        self.folderPath = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if self.folderPath != "":
            self.le_folderPath.setText(self.folderPath)

    def toggle_autoindexing(self):
        pass

    def save_capture_csv(self):
        if self.data is None:
            pass
        else:
            spectrum = self.data
            self.fileName = self.le_fileName.text()
            if self.fileName == "":
                self.fileName = "spectrum"

            fixedData = copy.deepcopy(spectrum)
            path = os.path.join(self.folderPath, f"{self.fileName}_x{self.widthId}_y{self.heightId}")
            if self.heightId is None and self.widthId is None:
                path = os.path.join(self.folderPath, f"{self.fileName}_background")
            with open(path + ".csv", "w+") as f:
                for i, x in enumerate(self.waves):
                    f.write(f"{x},{fixedData[i]}\n")
                f.close()

        if self.countSpectrum == self.width*self.height-1:
            spectra = self.matrixData
            self.fileName = self.le_fileName.text()
            if self.fileName == "":
                self.fileName = "acquisitions"

            fixedData = copy.deepcopy(spectra)
            path = os.path.join(self.folderPath, f"{self.fileName}_matrixData")
            with open(path + ".csv", "w+") as f:
                for i, x in enumerate(self.waves):
                    f.write(f"{x},{fixedData[i]}\n")
                f.close()

        # self.stop_save_thread()
