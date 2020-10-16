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

paramsViewUiPath = os.path.dirname(os.path.realpath(__file__)) + '\\paramsViewUi.ui'
Ui_paramsView, QtBaseClass = uic.loadUiType(paramsViewUiPath)

class ParametersView(QWidget, Ui_paramsView):  # type: QWidget

    def __init__(self, model=None, controller=None):
        super(ParametersView, self).__init__()
        self.setupUi(self)
        self.model = model
        self.selected_item_index = None
        with open(self.model.defaultFilePath, 'r') as fp:
            dictParameters = json.load(fp)
            self.temporaryParametersDict = dictParameters[0]
        self.plotDict = {}
        self.setup_table()
        self.connect_widgets()
        self.create_plots()

    def setup_table(self):
        self.tableModel = ParametersTableModel()
        self.tableView = ParametersTableView(self, self.tableModel)
        self.tableView.setObjectName("parametersTableView")
        self.tableWidgetLayout = QVBoxLayout()
        self.tableWidgetLayout.addWidget(self.tableView.table_view)
        self.tableWidget.setLayout(self.tableWidgetLayout)
        self.tableView.load_data(self.temporaryParametersDict)
        for row in range(self.tableModel.rowCount()):
            col = 0
            index = self.tableModel.index(row, col, QtCore.QModelIndex())
            value = '[all]'
            self.tableModel.setData(index, value, QtCore.Qt.EditRole)
        for i in range(self.tableModel.rowCount()):
            self.tableView.table_view.openPersistentEditor(self.tableModel.index(i, 0))

    def connect_widgets(self):
        self.pb_save.clicked.connect(self.save_parameters)
        self.tableModel.dataChanged.connect(self.update_data)
        self.rb_binomial.clicked.connect(self.update_distribution_type_in_dict)
        self.rb_geometric.clicked.connect(self.update_distribution_type_in_dict)
        self.rb_laplacian.clicked.connect(self.update_distribution_type_in_dict)
        self.rb_log.clicked.connect(self.update_distribution_type_in_dict)
        self.rb_negbinomial.clicked.connect(self.update_distribution_type_in_dict)
        self.rb_planck.clicked.connect(self.update_distribution_type_in_dict)
        self.rb_poisson.clicked.connect(self.update_distribution_type_in_dict)
        self.rb_uniform.clicked.connect(self.update_distribution_type_in_dict)
        self.rb_zipf.clicked.connect(self.update_distribution_type_in_dict)
        self.onSliderPress = 0
        self.sl_mean.setMaximum(100)
        self.sl_mean.setMinimum(0)
        self.sl_mean.setSingleStep(1)
        self.sl_sd.setMaximum(100)
        self.sl_sd.setMinimum(0)
        self.sl_sd.setSingleStep(1)
        self.sl_mean.sliderMoved.connect(lambda: self.set_on_sl_press(True))
        self.sl_mean.valueChanged.connect(lambda: self.update_slider_distribution_parameter(caller='sl'))
        self.sl_sd.sliderMoved.connect(lambda: self.set_on_sl_press(True))
        self.sl_sd.valueChanged.connect(lambda: self.update_slider_distribution_parameter(caller='sl'))
        self.tableView.table_model.s_data_changed.connect(self.update_slider_distribution_parameter)

    def create_plots(self):
        self.plotDict["plotItem"] = PlotItem()
        # self.plotDict["plotDataItem"] = self.plotDict["plotItem"].plot()
        self.pyqtgraphWidget.addItem(self.plotDict["plotItem"])
        self.plotDict["BarGraphItem"] = None

    def update_graph(self, dataDict):
        try:
            # emptyDict = {
            #     "x": [],
            #     "y": []
            # }
            if self.plotDict["BarGraphItem"] is not None:
                self.plotDict["plotItem"].removeItem(self.plotDict["BarGraphItem"])
            # if distributionType is None:
            #     self.plotDict["plotDataItem"].setData(**dataDict)
            # else:
            # self.plotDict["plotDataItem"].setData(**emptyDict)
            self.plotDict["BarGraphItem"] = BarGraphItem(x=dataDict["x"], height=dataDict["y"], width=0.4, brush='r')
            self.plotDict["plotItem"].addItem(self.plotDict["BarGraphItem"])
        except Exception as E:
            log.error(E)

    def generate_graph_data(self):
        ageGroup = self.tableModel.data[self.selected_item_index.row()][0]
        parameter = self.tableModel.data[self.selected_item_index.row()][1]
        p1 = self.temporaryParametersDict[ageGroup][parameter]["p1"]
        p2 = self.temporaryParametersDict[ageGroup][parameter]["p2"]

        distributionType = self.temporaryParametersDict[ageGroup][parameter]["distributionType"]
        xyDict = {"x": [],
                  "y": []}
        try:
            if distributionType == 'Binomial':
                xyDict["x"] = np.arange(binom.ppf(0.01, int(p1), p2/100), binom.ppf(0.99, int(p1), p2/100))
                xyDict["y"] = binom.pmf(xyDict["x"], int(p1), p2/100)
            elif distributionType == 'Geometric':
                xyDict["x"] = np.arange(geom.ppf(0.01, p1/100), geom.ppf(0.99, p1/100))
                xyDict["y"] = geom.pmf(xyDict["x"], p1/100)
                if p2 != 0:
                    self.tableModel.setData(self.selected_item_index.sibling(self.selected_item_index.row(), 3), 0,
                                            Qt.EditRole)
            elif distributionType == 'Laplacian':
                xyDict["x"] = np.arange(dlaplace.ppf(0.01, p1/100), dlaplace.ppf(0.99, p1/100))
                xyDict["y"] = dlaplace.pmf(xyDict["x"], p1/100)
                if p2 != 0:
                    self.tableModel.setData(self.selected_item_index.sibling(self.selected_item_index.row(), 3), 0,
                                            Qt.EditRole)
            elif distributionType == 'Logarithmic':
                xyDict["x"] = np.arange(logser.ppf(0.01, p1/100), logser.ppf(0.99, p1/100))
                xyDict["y"] = logser.pmf(xyDict["x"], p1/100)
                if p2 != 0:
                    self.tableModel.setData(self.selected_item_index.sibling(self.selected_item_index.row(), 3), 0,
                                            Qt.EditRole)
            elif distributionType == 'Neg. binomial':
                xyDict["x"] = np.arange(nbinom.ppf(0.01, p1, p2/100), nbinom.ppf(0.99, p1, p2/100))
                xyDict["y"] = nbinom.pmf(xyDict["x"], p1, p2/100)
            elif distributionType == 'Planck':
                xyDict["x"] = np.arange(planck.ppf(0.01, p1/100), planck.ppf(0.99, p1/100))
                xyDict["y"] = planck.pmf(xyDict["x"], p1/100)
                if p2 != 0:
                    self.tableModel.setData(self.selected_item_index.sibling(self.selected_item_index.row(), 3), 0,
                                            Qt.EditRole)
            elif distributionType == 'Poisson':
                xyDict["x"] = np.arange(poisson.ppf(0.01, p1), poisson.ppf(0.99, p1))
                xyDict["y"] = poisson.pmf(xyDict["x"], p1)
                if p2 != 0:
                    self.tableModel.setData(self.selected_item_index.sibling(self.selected_item_index.row(), 3), 0,
                                            Qt.EditRole)
            elif distributionType == 'Uniform':
                if p1-0.5*p2 < 0:
                    p2 = p1
                min = p1-0.5*p2
                max = p1+0.5*p2
                xyDict["x"] = np.arange(randint.ppf(0.01, min, max), randint.ppf(0.99, min, max))
                xyDict["y"] = randint.pmf(xyDict["x"], min, max)
            elif distributionType == 'Zipf (Zeta)':
                xyDict["x"] = np.arange(zipf.ppf(0.01, p1), zipf.ppf(0.99, p1))
                xyDict["y"] = zipf.pmf(xyDict["x"], p1)
                if p2 != 0:
                    self.tableModel.setData(self.selected_item_index.sibling(self.selected_item_index.row(), 3), 0,
                                            Qt.EditRole)
            self.update_graph(xyDict)
        except Exception as E:
            log.error(E)

    @pyqtSlot(QModelIndex)
    def update_data(self, index):
        try:
            if index.column() == 0:
                self.update_data_from_dict(index)
            else:
                self.update_dict_from_data(index)
        except Exception as E:
            log.error(E)

    def update_data_from_dict(self, index):
        ageGroup = self.tableModel.data[index.row()][0]
        parametersName = self.tableModel.data[index.row()][1]
        parametersindex1 = self.temporaryParametersDict[ageGroup][parametersName]['p1']
        parametersindex2 = self.temporaryParametersDict[ageGroup][parametersName]['p2']
        self.tableModel.setData(index.sibling(index.row(), 2), parametersindex1, Qt.EditRole)
        self.tableModel.setData(index.sibling(index.row(), 3), parametersindex2, Qt.EditRole)
        self.generate_graph_data()

    def update_dict_from_data(self, index):
        ageGroup = self.tableModel.data[index.row()][0]
        parametersName = self.tableModel.data[index.row()][1]
        parametersindex1 = self.tableModel.data[index.row()][2]
        parametersindex2 = self.tableModel.data[index.row()][3]
        self.temporaryParametersDict[ageGroup][parametersName]['p1'] = parametersindex1
        self.temporaryParametersDict[ageGroup][parametersName]['p2'] = parametersindex2
        self.generate_graph_data()

    def update_distribution_type_in_dict(self):
        try:
            ageGroup = self.tableModel.data[self.selected_item_index.row()][0]
            parameter = self.tableModel.data[self.selected_item_index.row()][1]
            if self.rb_binomial.isChecked():
                self.temporaryParametersDict[ageGroup][parameter]['distributionType'] = self.rb_binomial.text()
            elif self.rb_geometric.isChecked():
                self.temporaryParametersDict[ageGroup][parameter]['distributionType'] = self.rb_geometric.text()
            elif self.rb_laplacian.isChecked():
                self.temporaryParametersDict[ageGroup][parameter]['distributionType'] = self.rb_laplacian.text()
            elif self.rb_log.isChecked():
                self.temporaryParametersDict[ageGroup][parameter]['distributionType'] = self.rb_log.text()
            elif self.rb_negbinomial.isChecked():
                self.temporaryParametersDict[ageGroup][parameter]['distributionType'] = self.rb_negbinomial.text()
            elif self.rb_planck.isChecked():
                self.temporaryParametersDict[ageGroup][parameter]['distributionType'] = self.rb_planck.text()
            elif self.rb_poisson.isChecked():
                self.temporaryParametersDict[ageGroup][parameter]['distributionType'] = self.rb_poisson.text()
            elif self.rb_uniform.isChecked():
                self.temporaryParametersDict[ageGroup][parameter]['distributionType'] = self.rb_uniform.text()
            elif self.rb_zipf.isChecked():
                self.temporaryParametersDict[ageGroup][parameter]['distributionType'] = self.rb_zipf.text()

            self.generate_graph_data()
        except Exception as E:
            log.error(E)

    def set_distribution_type_value(self):
        try:
            ageGroup = self.tableModel.data[self.selected_item_index.row()][0]
            parameter = self.tableModel.data[self.selected_item_index.row()][1]
            distributionType = self.temporaryParametersDict[ageGroup][parameter]['distributionType']
            if distributionType == 'Binomial':
                self.rb_binomial.setChecked(True)
            elif distributionType == 'Geometric':
                self.rb_geometric.setChecked(True)
            elif distributionType == 'Laplacian':
                self.rb_laplacian.setChecked(True)
            elif distributionType == 'Logarithmic':
                self.rb_log.setChecked(True)
            elif distributionType == 'Neg. binomial':
                self.rb_negbinomial.setChecked(True)
            elif distributionType == 'Planck':
                self.rb_planck.setChecked(True)
            elif distributionType == 'Poisson':
                self.rb_poisson.setChecked(True)
            elif distributionType == 'Uniform':
                self.rb_uniform.setChecked(True)
            elif distributionType == 'Zipf (Zeta)':
                self.rb_zipf.setChecked(True)

        except Exception as E:
            log.error(E)

    def update_slider_distribution_parameter(self, caller=None, value=None):
        index = self.selected_item_index
        if caller == 'sl':
            if self.onSliderPress:
                p1 = self.sl_mean.value()
                p2 = self.sl_sd.value()
                self.tableModel.setData(index.sibling(index.row(), 2), p1, Qt.EditRole)
                self.tableModel.setData(index.sibling(index.row(), 3), p2, Qt.EditRole)
                self.set_on_sl_press(False)
        else:
            if not self.onSliderPress and value is None:
                self.sl_mean.setValue(self.tableModel.data[self.selected_item_index.row()][2])
                self.sl_sd.setValue(self.tableModel.data[self.selected_item_index.row()][3])

    def set_on_sl_press(self, value: bool):
        self.onSliderPress = value

    def save_parameters(self):
        defaultSimulationParametersJsonFilename = time.strftime("simulationParameters_%Y-%m-%d_%Hh%Mm%Ss.json")
        try:
            simulationParametersFilename, _ = \
                QFileDialog.getSaveFileName(directory=defaultSimulationParametersJsonFilename)
            with open(simulationParametersFilename, 'w') as fp:
                json.dump(self.temporaryParametersDict, fp)
        except Exception as E:
            log.error(E)

