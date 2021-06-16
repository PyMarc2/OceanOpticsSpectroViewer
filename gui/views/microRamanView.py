import numpy
from PyQt5.QtWidgets import QWidget
from PyQt5.Qt import QPixmap
from PyQt5.QtCore import pyqtSignal, Qt, QObject, QThread
from PyQt5 import uic
import os
from gui.modules import mockSpectrometer as mock
from tools.threadWorker import Worker



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

        self.hauteur = 0
        self.largeur = 0
        self.step = 0
        self.ordre = 1
        self.direction = 'other'
        self.exposureTime = 50
        self.AcqTime = 3000
        self.reset = False
        self.connect_widgets()
        #self.create_threads()
        #self.create_threads_acq()

        self.waves = None
        self.spec = None
        self.dataLen = None
        self.dataSep = 0
        self.isAcquisitionThreadAlive = False
        self.liveAcquisitionData = []
        self.isAcquisitionDone = False
        self.expositionCounter = 0
        self.integrationCountAcq = 0
        self.movingIntegrationData = None
        self.changeLastExposition = 0

    def create_threads_acq(self, *args):
        self.acqWorker = Worker(self.manage_data_flow, *args)
        self.acqWorker.moveToThread(self.acqThread)
        self.acqThread.started.connect(self.acqWorker.run)

    def create_threads(self):
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
        self.spinBox.textChanged.connect(self.image_size_1)
        self.spinBox_2.textChanged.connect(self.image_size_2)
        self.spinBox_3.textChanged.connect(self.displacement_step)
        self.comboBox.currentTextChanged.connect(self.measure_unit)
        self.pb_sweepSame.clicked.connect(self.sweep_same)
        self.pb_sweepAlternate.clicked.connect(self.sweep_other)
        self.pb_reset.clicked.connect(self.reset_acq)
        #self.pb_liveView.clicked.connect(self.sweep)
        self.sb_acqTime.textChanged.connect(self.set_acq_time)
        self.sb_exposure.textChanged.connect(self.set_exposure_time)

    def image_size_1(self):
        self.hauteur = self.spinBox.value()

    def image_size_2(self):
        self.largeur = self.spinBox_2.value()

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

    def reset_acq(self):
        self.reset = True
        #return True

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

    def sweep(self):
        pass

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

    def begin(self):
        for i in range(100):
            self.pb_reset.clicked.connect(self.resetAcq)
            if not self.reset:
                self.pb_reset.clicked.connect(self.resetAcq)
                self.disable_all_buttons()
                print(i)
            else:
                pass

        self.reset = False

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