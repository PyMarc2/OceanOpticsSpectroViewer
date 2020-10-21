from PyQt5.QtWidgets import QWidget, QMessageBox, QApplication, QCheckBox
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QThread
from PyQt5.Qt import QColor, QPalette
import os
from pyqtgraph import PlotItem, BarGraphItem
from pyqtgraph import GraphicsLayoutWidget
from PyQt5 import uic
import seabreeze.spectrometers as sb
from gui.modules import spectrometers as mock
from tools.threadWorker import Worker
from tools.CircularList import CircularList, RingBuffer
import numpy as np
import collections
import time

import logging


log = logging.getLogger(__name__)

filterViewUiPath = os.path.dirname(os.path.realpath(__file__)) + "\\filterViewUi.ui"
Ui_filterView, QtBaseClass = uic.loadUiType(filterViewUiPath)


class FilterView(QWidget, Ui_filterView):
    s_data_changed = pyqtSignal(dict)
    s_data_acquisition_done = pyqtSignal()

    # Initializing Functions

    def __init__(self, model=None, controller=None):
        super(FilterView, self).__init__()
        self.model = model
        self.setupUi(self)

        self.acqThread = QThread()
        self.plotItem = None
        self.dataPlotItem = None
        self.acqWorker = None
        self.spec = None
        self.waves = None
        self.exposureTime = 100
        self.integrationCount = 1
        self.displayData = None
        self.backgroundData = None
        self.acquisitionData = None
        self.analysedData = None
        self.isNormalized = None

        self.isAcqAlive = 0
        self.deviceConnected = 0
        self.normalizeData = 0
        self.launchBackgroundAcquire = 0
        self.backgroundAcquiring = 0
        self.backgroundRemove = 0
        self.backgroundWarningDisplay = 1
        self.expositionCounter = 0
        self.changeLastExposition = 0
        self.acquisitionDone = False

        self.integrationTimeViewRemainder_ms = 0
        self.integrationTimeAcqRemainder_ms = 0
        self.integrationCountAcq = 0
        self.integrationCountView = 0
        self.liveAcquisitionData = []
        self.movingIntegrationData = None

        self.create_dialogs()
        self.connect_buttons()
        self.connect_signals()
        self.connect_checkbox()
        self.create_threads()
        self.create_plots()
        self.initialize_device()
        self.update_indicators()

    def initialize_device(self):
        log.debug("Initializing devices...")
        try:
            devices = sb.list_devices()
            self.spec = sb.Spectrometer(devices[0])
            log.info("Devices:{}".format(devices))
            self.deviceConnected = True
        except IndexError as e:
            log.warning("No SpectrumDevice was found. Try connecting manually.")
            self.deviceConnected = False
            self.spec = mock.MockSpectrometer()
            log.info("No device found; Mocking Spectrometer Enabled.")

        self.set_exposure_time()

    def connect_buttons(self):
        self.pb_liveView.clicked.connect(self.toggle_live_view)

        self.pb_rmBackground.clicked.connect(self.save_background)
        self.pb_rmBackground.clicked.connect(self.update_indicators)

        self.pb_analyse.clicked.connect(lambda: setattr(self, "analysedData", True))
        self.pb_analyse.clicked.connect(lambda: setattr(self, "acquisitionData", True))
        self.pb_analyse.clicked.connect(self.update_indicators)

        self.pb_normalize.clicked.connect(lambda: setattr(self, "isNormalized", True))
        self.pb_normalize.clicked.connect(lambda: self.update_indicators())

        self.le_exposure.textChanged.connect(self.set_exposure_time)
        self.le_viewTime.textChanged.connect(self.set_integration_time)

        log.debug("Connecting GUI buttons...")

    def connect_checkbox(self):
        self.ind_rmBackground.clicked.connect(lambda:print("showBackground if available"))
        self.ind_normalize.clicked.connect(lambda: print("show normalisation if available"))
        self.ind_analyse.clicked.connect(lambda: print("show acquisition if available"))

    def connect_signals(self):
        log.debug("Connecting GUI signals...")
        self.s_data_changed.connect(self.update_graph)
        self.s_data_changed.connect(self.update_indicators)
        # self.s_data_acquisition_done.connect(self.update_indicators)

    def create_threads(self, *args):
        self.acqWorker = Worker(self.manage_data_flow, *args)
        self.acqWorker.moveToThread(self.acqThread)
        self.acqThread.started.connect(self.acqWorker.run)

    def create_dialogs(self):
        self.warningDialog = QMessageBox()
        self.warningDialog.setIcon(QMessageBox.Information)
        self.warningDialog.setText("Your light source should be 'OFF' before removing the background signal.")
        self.warningDialog.setWindowTitle("Remove Background")
        self.warningDialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        self.doNotShow = QCheckBox("Do not show again.")
        self.warningDialog.setCheckBox(self.doNotShow)
        self.doNotShow.clicked.connect(lambda: setattr(self, 'backgroundWarningDisplay', 0))

    def create_plots(self):
        log.debug("Creating GUI plots...")
        self.pyqtgraphWidget.clear()
        self.plotItem = self.pyqtgraphWidget.addPlot()
        self.dataPlotItem = self.plotItem.plot()

    # Low-Level Backend Functions

    @pyqtSlot(dict)
    def update_graph(self, plotData):
        y = plotData["y"]
        self.dataPlotItem.setData(self.waves, y)

    def manage_data_flow(self, *args, **kwargs):
        self.waves = self.spec.wavelengths()[2:]

        while self.isAcqAlive:

            if self.normalizeData:
                log.debug("should normalize data, equalize as well.")

            self.liveAcquisitionData = self.read_data_live().tolist()

            self.integrate_data()
            self.displayData = np.mean(np.array(self.movingIntegrationData()), 0)

            self.acquire_background()
            self.normalize_data()
            self.analyse_data()

            self.s_data_changed.emit({"y": self.displayData})

    def read_data_live(self, *args, **kwargs):
        return self.spec.intensities()[2:]

    def set_exposure_time(self, time_in_ms=None, update=True):
        try:
            if time_in_ms is None:
                self.exposureTime = int(self.le_exposure.text())
            else:
                self.exposureTime = int(time_in_ms)

            self.spec.integration_time_micros(self.exposureTime * 1000)
            self.le_exposure.setStyleSheet('color: black')
        except ValueError as e:
            self.le_exposure.setStyleSheet('color: red')
            log.error(e)
        if update:
            self.set_integration_time()

    def set_integration_time(self, time_in_ms_view=None, time_in_ms_acq=None):
        try:

            time_in_ms_view = self.le_viewTime.text()
            time_in_ms_acq = self.le_acqTime.text()

            integrationTimeView = int(time_in_ms_view)
            integrationTimeAcq = int(time_in_ms_acq)

            if integrationTimeView >= self.exposureTime:
                self.integrationCountView = integrationTimeView // self.exposureTime
                self.integrationCountAcq = integrationTimeAcq // self.exposureTime
                self.integrationTimeViewRemainder_ms = integrationTimeView-self.integrationCountView*self.exposureTime
                self.integrationTimeAcqRemainder_ms = integrationTimeAcq - self.integrationCountAcq * self.exposureTime
                self.le_viewTime.setStyleSheet('color: black')
            else:
                self.integrationCountView = 1
                self.le_viewTime.setStyleSheet('color: red')

        except ValueError as e:
            log.error(e)
            self.le_viewTime.setStyleSheet('color: red')

        if self.integrationTimeViewRemainder_ms > 3:
            self.movingIntegrationData = RingBuffer(size_max=self.integrationCountView+1)
            self.changeLastExposition = 1
        else:
            self.movingIntegrationData = RingBuffer(size_max=self.integrationCountView)
            self.changeLastExposition = 0

    def integrate_data(self):
        self.acquisitionDone = False
        if self.expositionCounter < self.integrationCountView - 1:
            self.movingIntegrationData.append(self.liveAcquisitionData)
            self.expositionCounter += 1

        elif self.expositionCounter == self.integrationCountView - 1:
            self.movingIntegrationData.append(self.liveAcquisitionData)
            self.expositionCounter += 1
            if self.changeLastExposition:
                self.set_exposure_time(self.integrationTimeViewRemainder_ms, update=False)
        else:
            self.movingIntegrationData.append(self.liveAcquisitionData)
            self.acquisitionDone = True
            self.expositionCounter = 0

    def acquire_background(self):
        if self.launchBackgroundAcquire and not self.backgroundAcquiring:
            self.expositionCounter = 0
            self.backgroundAcquiring = True
            self.launchBackgroundAcquire = False
            log.debug("Background Acquiring...")

        elif self.backgroundAcquiring:
            if not self.acquisitionDone:
                log.debug(
                    "Background frame: {} over {} : {}%".format(self.expositionCounter, self.integrationCountView,
                                                                int(
                                                                    self.expositionCounter * 100 / self.integrationCountView)))
            elif self.acquisitionDone:
                self.backgroundData = np.mean(np.array(self.movingIntegrationData()), 0)
                self.backgroundRemove = True
                self.backgroundAcquiring = False
                log.debug("Background acquired.")

        if self.backgroundRemove:
            self.displayData = self.displayData - self.backgroundData

    def normalize_data(self):
        pass

    def analyse_data(self):
        pass

    # High-Level Front-End Functions
    
    def toggle_live_view(self):
        if not self.isAcqAlive:
            try:
                self.acqThread.start()
                self.isAcqAlive = True
                self.pb_liveView.start_flash()
            except Exception as e:
                log.error(e)
                self.spec = mock.MockSpectrometer()

        else:
            self.acqThread.terminate()
            self.pb_liveView.stop_flash()
            self.isAcqAlive = False
        self.update_indicators()

    def visualize_any_acquisition(self):
        pass
        
    def update_indicators(self):
        if self.isAcqAlive:
            self.ind_rmBackground.setEnabled(True)
            self.ind_normalize.setEnabled(True)
            self.ind_analyse.setEnabled(True)
            self.enable_all_buttons()
            if self.backgroundData is None:
                self.ind_rmBackground.setStyleSheet("QCheckBox::indicator{background-color: #db1a1a;}")
                try:
                    self.ind_rmBackground.clicked.disconnect()
                except Exception:
                    pass
            else:
                self.ind_rmBackground.setStyleSheet("QCheckBox::indicator{background-color: #55b350;}")

            if self.backgroundAcquiring:
                self.ind_rmBackground.setStyleSheet("QCheckBox::indicator{background-color: #f79c34;}")

            if self.isNormalized is None:
                self.ind_normalize.setStyleSheet("QCheckBox::indicator{background-color: #db1a1a;}")
                try:
                    self.ind_normalize.clicked.disconnect()
                except Exception:
                    pass
            else:
                self.ind_normalize.setStyleSheet("QCheckBox::indicator{background-color: #55b350;}")

            if self.acquisitionData is None:
                self.ind_analyse.setStyleSheet("QCheckBox::indicator{background-color: #db1a1a;}")
                try:
                    self.ind_analyse.clicked.disconnect()
                except Exception:
                    pass
            else:
                self.ind_analyse.setStyleSheet("QCheckBox::indicator{background-color: #55b350;}")
        else:
            self.disable_all_buttons()
            self.ind_rmBackground.setEnabled(False)
            self.ind_normalize.setEnabled(False)
            self.ind_analyse.setEnabled(False)
            self.ind_rmBackground.setStyleSheet("QCheckBox::indicator{background-color: #9e9e9e;}")
            self.ind_normalize.setStyleSheet("QCheckBox::indicator{background-color: #9e9e9e;}")
            self.ind_analyse.setStyleSheet("QCheckBox::indicator{background-color: #9e9e9e;}")

    def disable_all_buttons(self):
        self.pb_rmBackground.setEnabled(False)
        self.pb_normalize.setEnabled(False)
        self.pb_analyse.setEnabled(False)

    def enable_all_buttons(self):
        self.pb_rmBackground.setEnabled(True)
        self.pb_normalize.setEnabled(True)
        self.pb_analyse.setEnabled(True)

    def save_background(self):
        if self.backgroundWarningDisplay:
            answer = self.warningDialog.exec_()
            if answer == QMessageBox.Ok:
                self.launchBackgroundAcquire = 1
            elif answer == QMessageBox.Cancel:
                log.debug("Background data not taken.")

        else:

            self.launchBackgroundAcquire = 1
            self.update_indicators()
            self.disable_all_buttons()


# TODO:
# remove background, normalize (take ref, create norm, norm stream)
# add wavelength line cursor with value display
