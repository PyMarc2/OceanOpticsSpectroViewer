import numpy
from PyQt5.QtWidgets import QWidget
from PyQt5.Qt import QPixmap
from PyQt5.QtCore import pyqtSignal, Qt, QObject, QThread
from PyQt5 import uic
import os
from gui.modules import mockSpectrometer as mock
from tools.threadWorker import Worker
import numpy as np
import logging


log = logging.getLogger(__name__)


microRamanViewUiPath = os.path.dirname(os.path.realpath(__file__)) + '{0}microRamanViewUi.ui'.format(os.sep)
print(microRamanViewUiPath)
Ui_microRamanView, QtBaseClass = uic.loadUiType(microRamanViewUiPath)


class MicroRamanView(QWidget, Ui_microRamanView):  # type: QWidget

    s_lens_data_changed = pyqtSignal(dict)

    def __init__(self, model=None, controller=None):
        super(MicroRamanView, self).__init__()
        self.setupUi(self)
        self.model = model
        self.plotItem = None
        self.dataPlotItem = None
        self.initialize_buttons()

        self.sweepThread = QThread()
        self.acqThread =QThread()
        self.isAcquisitionThreadAlive = False
        self.isSweepThreadAlive = False

        self.height = 0
        self.width = 0
        self.step = 0
        self.ordre = 1
        self.direction = 'other'
        self.exposureTime = 50
        self.AcqTime = 3000
        self.connect_widgets()
        self.create_threads()

        s_data_changed = pyqtSignal(dict)
        s_data_acquisition_done = pyqtSignal()
        self.isAcquiringNormalization = False
        self.isSpectrumNormalized = False
        self.isAcquiringIntegration = False
        self.isAcquiringBackground = False
        self.launchIntegrationAcquisition = False
        self.backgroundData = None
        self.temporaryIntegrationData = None
        self.isBackgroundRemoved = False
        self.displayData = None
        self.backgroundData = None
        self.waves = None
        self.spec = None
        self.dataLen = None
        self.dataSep = 0
        self.liveAcquisitionData = []
        self.isAcquisitionDone = False
        self.expositionCounter = 0
        self.integrationCountAcq = 0
        self.movingIntegrationData = None
        self.changeLastExposition = 0
        self.normalizationMultiplierList = []
        self.normalizationData = None
        self.errorRejectedList = None
        self.maxAcceptedAbsErrorValues = 0.01
        self.rejectedXValues = []
        self.errorRegionsIndexesLimits = []
        self.errorRegionsLimits = []
        self.pyqtRegionList = []

    def create_threads(self, *args):
        self.acqWorker = Worker(self.manage_data_flow, *args)
        self.acqWorker.moveToThread(self.acqThread)
        self.acqThread.started.connect(self.acqWorker.run)

        self.sweepWorker = Worker(self.sweep, *args)
        self.sweepWorker.moveToThread(self.sweepThread)
        self.sweepThread.started.connect(self.sweepWorker.run)

    def initialize_buttons(self):
        self.pb_sweepSame.setIcons(QPixmap("./gui/misc/icons/sweep_same.png").scaled(50, 50,Qt.KeepAspectRatio, Qt.SmoothTransformation),
                                   QPixmap("./gui/misc/icons/sweep_same_hover.png").scaled(50, 50,Qt.KeepAspectRatio, Qt.SmoothTransformation),
                                   QPixmap("./gui/misc/icons/sweep_same_clicked.png").scaled(50, 50,Qt.KeepAspectRatio, Qt.SmoothTransformation),
                                   QPixmap("./gui/misc/icons/sweep_same_selected.png").scaled(50, 50,Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.pb_sweepAlternate.setIcons(QPixmap("./gui/misc/icons/sweep_alternate.png").scaled(50, 50,Qt.KeepAspectRatio, Qt.SmoothTransformation),
                                   QPixmap("./gui/misc/icons/sweep_alternate_hover.png").scaled(50, 50,Qt.KeepAspectRatio, Qt.SmoothTransformation),
                                   QPixmap("./gui/misc/icons/sweep_alternate_clicked.png").scaled(50, 50,Qt.KeepAspectRatio, Qt.SmoothTransformation),
                                   QPixmap("./gui/misc/icons/sweep_alternate_selected.png").scaled(50, 50,Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def connect_widgets(self):
        self.sb_height.textChanged.connect(self.image_height)
        self.sb_width.textChanged.connect(self.image_width)
        self.sb_step.textChanged.connect(self.displacement_step)
        self.cmb_magnitude.currentTextChanged.connect(self.measure_unit)
        self.pb_sweepSame.clicked.connect(self.sweep_same)
        self.pb_sweepAlternate.clicked.connect(self.sweep_other)
        self.pb_reset.clicked.connect(self.stop_acq)
        self.pb_liveView.clicked.connect(self.begin)
        self.sb_acqTime.textChanged.connect(self.set_acq_time)
        self.sb_exposure.textChanged.connect(self.set_exposure_time)

    def image_height(self):
        self.height = self.spinBox.value()

    def image_width(self):
        self.width = self.spinBox_2.value()

    def displacement_step(self):
        self.step = self.spinBox_3.value()

    def measure_unit(self):
        if self.comboBox.currentText() == 'mm':
            self.ordre = 10**3

        elif self.comboBox.currentText() == 'um':
            self.ordre = 1

        elif self.comboBox.currentText() == 'nm':
            self.ordre = 10**(-3)

    def sweep_same(self):
        self.direction = 'same'

    def sweep_other(self):
        self.direction = 'other'

    def set_exposure_time(self):
        self.exposureTime = self.sb_exposure.value()

    def set_acq_time(self):
        self.AcqTime = self.sb_acqTime.value()

    def disable_all_buttons(self):
        self.spinBox.setEnabled(False)
        self.spinBox_2.setEnabled(False)
        self.spinBox_3.setEnabled(False)
        self.comboBox.setEnabled(False)
        self.pb_sweepSame.setEnabled(False)
        self.pb_sweepAlternate.setEnabled(False)
        self.sb_exposure.setEnabled(False)
        self.sb_acqTime.setEnabled(False)

    def enable_all_buttons(self):
        self.spinBox.setEnabled(True)
        self.spinBox_2.setEnabled(True)
        self.spinBox_3.setEnabled(True)
        self.comboBox.setEnabled(True)
        self.pb_sweepSame.setEnabled(True)
        self.pb_sweepAlternate.setEnabled(True)
        self.sb_exposure.setEnabled(True)
        self.sb_acqTime.setEnabled(True)

    def read_data_live(self, *args, **kwargs):
        return self.spec.intensities()[2:]

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

    def launch_integration_acquisition(self):
        if self.launchIntegrationAcquisition and not self.isAcquiringIntegration:
            self.expositionCounter = 0
            self.isAcquiringIntegration = True
            self.launchIntegrationAcquisition = False
            #log.info("Integration Acquiring...")

        elif self.isAcquiringIntegration:
            if not self.isAcquisitionDone:
                percent = int(self.expositionCounter * 100 / self.integrationCountAcq)
                if percent in [25, 50, 75, 100]:
                    log.debug(
                    "Acquisition frame: {} over {} : {}%".format(self.expositionCounter, self.integrationCountAcq,
                                                                int(self.expositionCounter * 100 / self.integrationCountAcq)))
            elif self.isAcquisitionDone:
                self.temporaryIntegrationData = np.mean(np.array(self.movingIntegrationData()), 0)
                self.isAcquiringIntegration = False
                log.debug("Integration acquired.")

    def segregate_same_regions(inputList, sep):
        listOfRegions = [[]]
        listOfRegionsIndexes = [[]]
        newRegion = 0
        for i, v in enumerate(inputList):

            if i == 0:
                if inputList[1] <= inputList[0] + sep:
                    listOfRegions[-1].append(inputList[0])
                    listOfRegionsIndexes[-1].append(int(i))

            elif inputList[i] <= inputList[i - 1] + sep:
                if newRegion:
                    listOfRegions[-1].append(inputList[i - 1])
                    listOfRegionsIndexes[-1].append(int(i - 1))
                    newRegion = 0
                listOfRegions[-1].append(inputList[i])
                listOfRegionsIndexes[-1].append(int(i))

            else:
                listOfRegions.append([])
                listOfRegionsIndexes.append([])
                newRegion = 1

        listOfLimits = []
        listOfIndexesLimits = []
        if listOfRegions:
            for i, region in enumerate(listOfRegions):
                if region:
                    listOfLimits.append([min(region), max(region)])
                    listOfIndexesLimits.append([min(listOfRegionsIndexes[i]), max(listOfRegionsIndexes[i])])

        return listOfLimits, listOfRegions, listOfRegionsIndexes, listOfIndexesLimits

    def acquire_background(self):
        if self.isAcquiringBackground:
            self.launchIntegrationAcquisition = True
            self.launch_integration_acquisition()

            if self.isAcquisitionDone:
                self.backgroundData = self.temporaryIntegrationData
                self.isBackgroundRemoved = True
                self.isAcquiringBackground = False
                log.info("Background acquired.")

        if self.isBackgroundRemoved:
            self.displayData = self.displayData - self.backgroundData

    def normalize_data(self):
        if self.isAcquiringNormalization:
            self.launchIntegrationAcquisition = True
            self.launch_integration_acquisition()

            if self.isAcquisitionDone:
                self.normalizationMultiplierList = []
                self.normalizationData = self.displayData
                maximumCount = max(self.normalizationData)
                for i in self.normalizationData:
                    if i != 0:
                        self.normalizationMultiplierList.append(float(1 / i))
                    else:
                        self.normalizationMultiplierList.append(0)

                self.isSpectrumNormalized = True
                self.isAcquiringNormalization = False
                log.info("Normalization Spectrum acquired.")
                self.plotItem.setRange(yRange=[0, 1.1])
                self.draw_error_regions()

        if self.isSpectrumNormalized:
            self.displayData = [a * b for a, b in zip(self.displayData, self.normalizationMultiplierList)]

    def draw_error_regions(self):
        self.verify_absolute_error()
        self.remove_old_error_regions()
        self.find_error_regions()
        self.add_error_regions()

    def verify_absolute_error(self):
        if self.isSpectrumNormalized:
            brute = np.array(self.movingIntegrationData()) * np.array(self.normalizationMultiplierList)
            sd = np.std(brute, axis=0)
            # log.debug("Standard Deviation of points:{}".format(sd))
            self.errorRejectedList = []
            counter = 0
            for i, error in enumerate(sd):
                if error >= self.maxAcceptedAbsErrorValue:
                    self.errorRejectedList.append(True)
                else:
                    self.errorRejectedList.append(False)
                    counter += 1
            self.rejectedXValues = self.waves[self.errorRejectedList]
            log.debug("Amount of accepted values:{}".format(counter))

    def find_error_regions(self):
        regionsLimits, regionPoints, regionIndexes, regionIndexesLimits = self.segregate_same_regions(
            self.rejectedXValues, 15 * self.dataSep)

        self.errorRegionsIndexesLimits = regionIndexesLimits
        self.errorRegionsLimits = regionsLimits
        log.debug("Rejected Regions:{}".format(self.errorRegionsLimits))

    def add_error_regions(self):
        try:
            self.pyqtRegionList = []
            for region in self.errorRegionsLimits:
                errorRegion = LinearRegionItem(brush=self.errorBrush, pen=self.errorPen, movable=False)
                errorRegion.setRegion(region)
                self.pyqtRegionList.append(errorRegion)
                self.plotItem.addItem(self.pyqtRegionList[-1])
        except Exception as e:
            log.error(e)

    def remove_old_error_regions(self):
        try:
            for region in self.pyqtRegionList:
                self.plotItem.removeItem(region)
        except Exception as e:
            log.error(e)

    def hide_high_error_values(self):
        if self.isSpectrumNormalized:
            # log.debug(self.errorRegionIndexesLimits)
            for region in self.errorRegionIndexesLimits:
                for i in range(region[0], region[1]):
                    self.displayData[i] = self.displayData[i] * 0

    def analyse_data(self):
        pass

    def manage_data_flow(self, *args, **kwargs):
        self.waves = self.spec.wavelengths()[2:]
        self.dataLen = len(self.waves)
        self.dataSep = (max(self.waves) - min(self.waves)) / len(self.waves)

        while self.isAcquisitionThreadAlive:
            self.liveAcquisitionData = self.read_data_live().tolist()

            self.integrate_data()
            self.displayData = np.mean(np.array(self.movingIntegrationData()), 0)

            self.acquire_background()
            self.normalize_data()
            self.hide_high_error_values()
            self.analyse_data()

            self.s_data_changed.emit({"y": self.displayData})

    def sweep(self, *args, **kwargs):
        self.count = 0
        while self.isSweepThreadAlive:
            self.count += 1

    def begin(self):
        if not self.isSweepThreadAlive:
            try:
                self.sweepThread.start()
                self.isSweepThreadAlive = True
                #self.pb_liveView.start_flash()

            except Exception as e:
                self.spec = mock.MockSpectrometer()

        else:
            print('Sampling already started')

    def stop_acq(self):
        self.sweepThread.terminate()
        # self.pb_liveView.stop_flash()
        self.isSweepThreadAlive = False


    """
    def connect_signals(self):
        log.debug("Connecting GUI signals...")
        self.s_data_changed.connect(self.update_graph)
        self.s_data_changed.connect(self.update_indicators)
        # self.s_data_acquisition_done.connect(self.update_indicators)
    
    def reset(self):
           self.dataPlotItem.clear()
           self.remove_old_error_regions()
           self.plotItem.setRange(xRange=self.xPlotRange, yRange=self.yPlotRange)
           self.backgroundData = None
           self.isBackgroundRemoved = False
           self.normalizationData = None
           self.normalizationMultiplierList = None
           self.isSpectrumNormalized = False
           self.update_indicators()
           log.info("All parameters and acquisition reset.")
    """

    # Data Capture Methods

    """
    def select_save_folder(self):
        self.folderPath = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        if self.folderPath != "":
            self.le_folderPath.setText(self.folderPath)

    def toggle_autoindexing(self):
        pass

    def save_capture_csv(self):
        self.fileName = self.le_fileName.text()
        if self.folderPath == "":
            pass

        elif self.fileName == "":
            pass

        else:
            fixedData = copy.deepcopy(self.displayData)
            path = os.path.join(self.folderPath, self.fileName)
            with open(path + ".csv", "w+") as f:
                for i, x in enumerate(self.waves):
                    f.write(f"{x},{fixedData[i]}\n")
                f.close()
    """