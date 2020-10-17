from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFileDialog, QMessageBox
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QModelIndex, Qt, QAbstractItemModel
from pyqtgraph import PlotItem, BarGraphItem
from gui.widgets.parametersTableWidget import ParametersTableModel
from gui.widgets.parametersTableWidget import ParametersTableView
from PyQt5 import uic, QtCore
from scipy.stats import binom, geom, dlaplace, logser, nbinom, poisson, planck, randint, zipf
import numpy as np
import logging
import json
import time
import os

log = logging.getLogger(__name__)

lensViewUiPath = os.path.dirname(os.path.realpath(__file__)) + '\\lensViewUi.ui'
Ui_lensView, QtBaseClass = uic.loadUiType(lensViewUiPath)


class LensView(QWidget, Ui_lensView):  # type: QWidget

    s_lens_data_changed = pyqtSignal(dict)

    def __init__(self, model=None, controller=None):
        super(LensView, self).__init__()
        self.setupUi(self)
        self.model = model
        self.plotItem = None
        self.dataPlotItem = None
        self.connect_widgets()
        self.create_plots()

    def connect_widgets(self):
        pass

    def connect_signals(self):
        log.info("Connecting simulationView Signals...")
        self.s_lens_data_changed.connect(self.update_graph)

    def create_plots(self):
        self.pyqtgraphWidget.clear()
        self.plotItem = self.pyqtgraphWidget.addPlot()
        self.dataPlotItem = self.plotItem.plot()

    @pyqtSlot(dict)
    def update_graph(self, plotData):
        x = plotData["x"]
        y = plotData["y"]
        self.dataPlotItem.setData(x, y)
