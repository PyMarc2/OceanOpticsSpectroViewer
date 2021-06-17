import numpy
from PyQt5.QtWidgets import QWidget
from PyQt5.Qt import QPixmap
from PyQt5.QtCore import pyqtSignal, Qt, QObject, QThread
from PyQt5 import uic
import os
from gui.modules import mockSpectrometer as mock
from tools.threadWorker import Worker
from tools.CircularList import RingBuffer
import numpy as np
import logging


log = logging.getLogger(__name__)


microRamanViewUiPath = os.path.dirname(os.path.realpath(__file__)) + '{0}microRamanViewUi.ui'.format(os.sep)
print(microRamanViewUiPath)
Ui_microRamanView, QtBaseClass = uic.loadUiType(microRamanViewUiPath)


class MicroRamanView(QWidget, Ui_microRamanView):  # type: QWidget

    s_data_changed = pyqtSignal(dict)
    s_data_acquisition_done = pyqtSignal()

    def __init__(self, model=None, controller=None):
        super(MicroRamanView, self).__init__()
        self.setupUi(self)
        self.model = model
        self.plotItem = None
        self.dataPlotItem = None
        self.initialize_buttons()

        self.sweepThread = QThread()
        self.isAcquisitionThreadAlive = False
        self.isSweepThreadAlive = False
        self.saveThread = Qthread()

        self.height = 0
        self.width = 0
        self.step = 0
        self.ordre = 1
        self.direction = 'other'
        self.exposureTime = 50
        self.integrationTimeAcq = 3000
        self.acqTimeRemainder_ms = 0
        self.connect_widgets()
        self.create_threads()

        self.countIntegrationWhile = 0
        self.isAcquiringIntegration = False
        self.temporaryIntegrationData = None
        self.spec = None
        self.liveAcquisitionData = []
        self.isAcquisitionDone = False
        self.integrationCountAcq = 0
        self.dataLive = []
        self.matriceDonnesBrutes = []

    #on va devoir changer le sweepthread pour un savethread, qui servira uniquement à l'enregistrement des données,
    #sinon le sweep et acquisition sont la même chose finalement
    def create_threads(self, *args):
        self.sweepWorker = Worker(self.sweep, *args)
        self.sweepWorker.moveToThread(self.sweepThread)
        self.sweepThread.started.connect(self.sweepWorker.run)

        """
        self.saveWorker = Worker(self.save, *args)
        self.saveWorker.moveToThread(self.saveThread)
        self.saveThread.started.connect(self.saveWorker.run)
        """

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

    def measure_unit(self):
        if self.cmb_magnitude.currentText() == 'mm':
            self.ordre = 10**3

        elif self.cmb_magnitude.currentText() == 'um':
            self.ordre = 1

        elif self.cmb_magnitude.currentText() == 'nm':
            self.ordre = 10**(-3)

        else:
            print('What the hell is going on?')

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

    def set_exposure_time(self):
        expositionTime = self.exposureTime
        self.spec.integration_time_micros(expositionTime * 1000)

    def set_integration_time(self, time_in_ms_view=None, time_in_ms_acq=None):
        try:
            if self.integrationTimeAcq >= self.exposureTime:
                self.integrationCountAcq = self.integrationTimeAcq // self.exposureTime
                self.integrationTimeAcqRemainder_ms = self.integrationTimeAcq - (
                            self.integrationCountAcq * self.exposureTime)
            else:
                self.integrationCountAcq = 1

        except ValueError as e:
            self.sb_acqTime.setStyleSheet('color: red')

    def read_data_live(self, *args, **kwargs):
        return self.spec.intensities()[2:]

    def launch_integration_acquisition(self):
        if self.launchIntegrationAcquisition and not self.isAcquiringIntegration:
            self.isAcquiringIntegration = True
            self.isAcquisitionDone = False

        elif self.isAcquiringIntegration:
            if not self.isAcquisitionDone:
                pass

            elif self.isAcquisitionDone:
                self.isAcquiringIntegration = False

    def SpectrumAcquisition(self):#Pas optimal avec la boucle en discuter avec MARC (boucle while + count?)
        self.launch_integration_acquisition()
        for i in range(integrationCountAcq):
            self.dataLive.append(self.read_data_live)
        self.matriceDonnesBrutes.append(dataLive)# il faudrait l'envoyé au bon endroit... comment faire?
        self.dataLive = []
        self.isAcquisitionDone = True
        self.launch_integration_acquisition()

    #ce sera ta fonction ça Benjamin, on pourrait changer le nom
    def sweep(self, *args, **kwargs):
        self.countHeight = 0
        self.countWidth = 0
        self.countSpectrums = 0
        while self.isSweepThreadAlive:
            if self.countSpectrums < self.width*self.height:
                pass
            else:
                self.isSweepThreadAlive = False
            self.countSpectrums += 1
    #il faudra connecter le signal de fin à move_stage, une fonction que je vais créer

    #on veut donc activer acquisitionthread (sweepthread n'existera plus)
    def begin(self):
        if not self.isSweepThreadAlive:
            try:
                self.disable_all_buttons()
                self.sweepThread.start()
                self.isSweepThreadAlive = True

            except Exception as e:
                self.spec = mock.MockSpectrometer()

        else:
            print('Sampling already started.')

    def stop_acq(self):
        if self.isSweepThreadAlive:
            self.sweepThread.terminate()
            # self.pb_liveView.stop_flash()
        else:
            print('Sampling already stopped.')

        self.isSweepThreadAlive = False
        self.enable_all_buttons()

    def move_stage(self):
        pass
        #va manquer à importer le fichier de commnucation avec le stage

    def save(self):
        pass

    """
    def connect_signals(self):
        log.debug("Connecting GUI signals...")
        self.s_data_changed.connect(self.update_graph)
        self.s_data_changed.connect(self.update_indicators)
        # self.s_data_acquisition_done.connect(self.update_indicators)
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