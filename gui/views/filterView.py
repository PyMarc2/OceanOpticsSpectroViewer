from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QThread
import os
from pyqtgraph import PlotItem, BarGraphItem
from pyqtgraph import GraphicsLayoutWidget
from PyQt5 import uic
import seabreeze.spectrometers as sb
from tools.threadWorker import Worker

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
        self.isAcqAlive = 0
        self.deviceConnected = 0

        self.make_threads()
        self.create_plots()
        self.initialize_device()

    def initialize_device(self):
        try:
            devices = sb.list_devices()
            self.spec = sb.Spectrometer(devices[0])
            self.spec.integration_time_micros(int(self.le_acqTime.text()) * 1000)
            log.info(devices)
            self.deviceConnected = True
        except IndexError as e:
            log.warning("No SpectrumDevice was found. Try connecting manually.")
            self.deviceConnected = False

    def connect_buttons(self):
        self.pb_liveView.clicked.connect(self.toggle_liveView)
        self.pb_analyse.clicked.connect(lambda: print("lol compute computer"))
        self.pb_normalize.clicked.connect(lambda: print("lol compute filter"))
        log.info("Connecting GUI widgets...")

    def connect_checkbox(self):
        pass

    def connect_signals(self):
        log.info("Connecting simulationView Signals...")
        self.s_data_changed.connect(self.update_graph)

    def create_plots(self):
        self.pyqtgraphWidget.clear()
        self.plotItem = self.pyqtgraphWidget.addPlot()
        self.dataPlotItem = self.plotItem.plot()

    @pyqtSlot(dict)
    def update_graph(self, plotData):
        x = plotData["x"]
        y = plotData["y"]
        self.dataPlotItem.setData(x, y)

    def read_data_live(self, *args, **kwargs):
        while self.isAcqAlive:
            waves = self.spec.wavelengths()[2:]
            intens = self.spec.intensities()[2:]
            self.s_data_changed.emit({"x": waves, "y": intens})

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

        else:
            self.acqThread.terminate()
            self.pb_liveView.stop_flash()
            self.isAcqAlive = False