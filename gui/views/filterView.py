from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QThread
import os
from pyqtgraph import PlotItem, BarGraphItem
from pyqtgraph import GraphicsLayoutWidget
from PyQt5 import uic
import seabreeze.spectrometers as sb
from gui.modules import spectrometers as mock
from tools.threadWorker import Worker
import numpy as np

import logging


log = logging.getLogger(__name__)

filterViewUiPath = os.path.dirname(os.path.realpath(__file__)) + "\\filterViewUi.ui"
Ui_filterView, QtBaseClass = uic.loadUiType(filterViewUiPath)


class FilterView(QWidget, Ui_filterView):
    s_data_changed = pyqtSignal(dict)

    def __init__(self, model=None, controller=None):
        super(FilterView, self).__init__()
        self.model = model
        self.setupUi(self)

        self.connect_buttons()
        self.connect_signals()
        self.connect_checkbox()

        self.acqThread = QThread()
        self.plotItem = None
        self.dataPlotItem = None
        self.acqWorker = None
        self.spec = None
        self.waves = None
        self.exposure_time = 100
        self.integration_count = 1
        self.isAcqAlive = 0
        self.deviceConnected = 0

        self.make_threads()
        self.create_plots()
        self.initialize_device()

    def initialize_device(self):
        log.debug("Initializing devices...")
        try:
            devices = sb.list_devices()
            self.spec = sb.Spectrometer(devices[0])
            log.info(devices)
            self.deviceConnected = True
        except IndexError as e:
            log.warning("No SpectrumDevice was found. Try connecting manually.")
            self.deviceConnected = False
            self.spec = mock.MockSpectrometer()

        self.spec.integration_time_micros(int(float(self.le_exposure.text()) * 1000))

    def connect_buttons(self):
        self.pb_liveView.clicked.connect(self.toggle_liveView)
        self.pb_analyse.clicked.connect(lambda: print("lol compute computer"))
        self.pb_normalize.clicked.connect(lambda: print("lol compute filter"))
        self.le_exposure.textChanged.connect(self.set_exposure_time)
        self.le_viewTime.textChanged.connect(self.set_integration_time)

        log.debug("Connecting GUI buttons...")

    def connect_checkbox(self):
        pass

    def connect_signals(self):
        log.debug("Connecting GUI signals...")
        self.s_data_changed.connect(self.update_graph)

    def create_plots(self):
        log.debug("Creating GUI plots...")
        self.pyqtgraphWidget.clear()
        self.plotItem = self.pyqtgraphWidget.addPlot()
        self.dataPlotItem = self.plotItem.plot()

    @pyqtSlot(dict)
    def update_graph(self, plotData):
        y = plotData["y"]
        self.dataPlotItem.setData(self.waves, y)

    def read_data_live(self, *args, **kwargs):
        self.waves = self.spec.wavelengths()[2:]

        while self.isAcqAlive:
            intens = []
            for _ in range(self.integration_count):
                intens.append(self.spec.intensities()[2:])
            intens = np.mean(intens, axis=0)
            self.s_data_changed.emit({"y": intens})

    def make_threads(self, *args):
        self.acqWorker = Worker(self.read_data_live, *args)
        self.acqWorker.moveToThread(self.acqThread)
        self.acqThread.started.connect(self.acqWorker.run)

    def toggle_liveView(self):
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

    def set_exposure_time(self, time_in_ms):
        try:
            self.exposure_time = int(time_in_ms)
            self.spec.integration_time_micros(self.exposure_time * 1000)
            self.le_exposure.setStyleSheet('color: black')
        except ValueError as e:
            self.le_exposure.setStyleSheet('color: red')
            log.error(e)

        self.set_integration_time()

    def set_integration_time(self, time_in_ms=None):
        try:
            if not time_in_ms:
                time_in_ms = self.le_viewTime.text()

            integration_time = int(time_in_ms)
            if integration_time >= self.exposure_time:
                self.integration_count = integration_time // self.exposure_time
                self.le_viewTime.setStyleSheet('color: black')
            else:
                self.integration_count = 1
                self.le_viewTime.setStyleSheet('color: red')
                # self.le_viewTime.setText(str(self.exposure_time))
        except ValueError as e:
            log.error(e)
            self.le_viewTime.setStyleSheet('color: red')

# TODO:
# remove background, normalize (take ref, create norm, norm stream)
# add wavelength line cursor with value display
