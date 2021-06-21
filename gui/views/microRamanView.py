import numpy
from PyQt5.QtWidgets import QWidget
from PyQt5.Qt import QPixmap
from PyQt5.QtCore import pyqtSignal, Qt, QObject, QThreadPool, QThread
from PyQt5 import uic
import os
from gui.modules import mockSpectrometer as mock
from tools.threadWorker import Worker
from tools.CircularList import RingBuffer
import numpy as np
from numpy import trapz
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

        self.threadpool = QThreadPool()
        self.isAcquisitionThreadAlive = False
        self.isSweepThreadAlive = False

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

        self.dataSep = 0
        self.countIntegrationWhile = 0
        self.integrationCountAcq = 0
        self.expositionCounter = 0
        self.integrationTimeAcqRemainder_ms = 0
        self.changeLastExposition = 0
        self.isAcquiringIntegration = False
        self.isAcquisitionDone = False
        self.isAcquiringBackground = False
        self.launchIntegrationAcquisition = False
        self.temporaryIntegrationData = None
        self.movingIntegrationData = None
        self.backgroundData = None
        self.spec = None
        self.waves = None
        self.dataLen = None
        self.actualPosition = None
        self.matrixData = None
        self.matrixRGB = None
        self.dataPixel = []
        self.liveAcquisitionData = []

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

    def connect_signals(self):
        self.s_data_changed.connect(self.move_stage)

    def create_threads(self, *args):
        self.sweepWorker = Worker(self.sweep, *args)
        self.sweepThread = QThread()
        self.sweepWorker.moveToThread(self.sweepThread)
        self.sweepThread.started.connect(self.sweepWorker.run)

        self.saveWorker = Worker(self.save, *args)
        self.saveThread = QThread()
        self.saveWorker.moveToThread(self.saveThread)
        self.saveThread.started.connect(self.saveWorker.run)

    def create_matrixData(self):
        self.matrixData = np.zeros((self.height, self.width), dtype=object)

    def create_matrixRGB(self):
        self.matrixRGB = np.zeros((self.height, self.width, 3), dtype=np.uint8)

    def initialize_buttons(self):
        self.pb_sweepSame.setIcons(QPixmap("./gui/misc/icons/sweep_same.png").scaled(50, 50,Qt.KeepAspectRatio, Qt.SmoothTransformation),
                                   QPixmap("./gui/misc/icons/sweep_same_hover.png").scaled(50, 50,Qt.KeepAspectRatio, Qt.SmoothTransformation),
                                   QPixmap("./gui/misc/icons/sweep_same_clicked.png").scaled(50, 50,Qt.KeepAspectRatio, Qt.SmoothTransformation),
                                   QPixmap("./gui/misc/icons/sweep_same_selected.png").scaled(50, 50,Qt.KeepAspectRatio, Qt.SmoothTransformation))
        self.pb_sweepAlternate.setIcons(QPixmap("./gui/misc/icons/sweep_alternate.png").scaled(50, 50,Qt.KeepAspectRatio, Qt.SmoothTransformation),
                                   QPixmap("./gui/misc/icons/sweep_alternate_hover.png").scaled(50, 50,Qt.KeepAspectRatio, Qt.SmoothTransformation),
                                   QPixmap("./gui/misc/icons/sweep_alternate_clicked.png").scaled(50, 50,Qt.KeepAspectRatio, Qt.SmoothTransformation),
                                   QPixmap("./gui/misc/icons/sweep_alternate_selected.png").scaled(50, 50,Qt.KeepAspectRatio, Qt.SmoothTransformation))

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
            self.ordre = 10**3

        elif self.cmb_magnitude.currentText() == 'um':
            self.ordre = 1

        elif self.cmb_magnitude.currentText() == 'nm':
            self.ordre = 10**(-3)

        else:
            print('What the hell is going on?!')

    def disable_all_buttons(self):
        self.sb_height.setEnabled(False)
        self.sb_width.setEnabled(False)
        self.sb_step.setEnabled(False)
        self.cmb_magnitude.setEnabled(False)
        self.pb_sweepSame.setEnabled(False)
        self.pb_sweepAlternate.setEnabled(False)
        self.sb_exposure.setEnabled(False)
        self.sb_acqTime.setEnabled(False)
        #self.pb_sweepSame.setFlat(True)
        #self.pb_sweepAlternate.setFlat(True)

    def enable_all_buttons(self):
        self.sb_height.setEnabled(True)
        self.sb_width.setEnabled(True)
        self.sb_step.setEnabled(True)
        self.cmb_magnitude.setEnabled(True)
        self.pb_sweepSame.setEnabled(True)
        self.pb_sweepAlternate.setEnabled(True)
        self.sb_exposure.setEnabled(True)
        self.sb_acqTime.setEnabled(True)
        #self.pb_sweepSame.setFlat(False)
        #self.pb_sweepAlternate.setFlat(False)

    def set_exposure_time(self):
        expositionTime = self.exposureTime
        self.spec.integration_time_micros(expositionTime * 1000)

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

    def spectrum_pixel_acquisition(self):#l'équivalent de manage_data_flow
        self.waves = self.spec.wavelengths()[2:]
        self.dataLen = len(self.waves)
        self.dataSep = (max(self.waves) - min(self.waves)) / len(self.waves)

        self.liveAcquisitionData = self.read_data_live().tolist()

        self.integrate_data()
        self.dataPixel = np.mean(np.array(self.movingIntegrationData()), 0)
        self.acquire_background()

    def matrixData_replace(self):# Mettre le dataPixel au bon endroit dans la matrice
        self.matrixData[self.countHeight][self.countWidth] = np.array(self.dataPixel)

    def matrixRGB_replace(self):
        self.dataPixel = np.array(self.dataPixel) / max(self.dataPixel)
        R, G, B = np.array_split(self.dataPixel, 3)
        areaR = trapz(R, dx=1)
        areaG = trapz(G, dx=1)
        areaB = trapz(B, dx=1)

        areas = np.array([areaR, areaG, areaB])
        areas = (areas / max(areas))*255
        self.matrixRGB[self.countHeight, self.countWidth, :] = areas

        self.dataPixel = []
        self.s_data_changed.emit({f"{self.countSpectrums}": self.dataPixel})  # était avant à la fin de la fonction prédédente, soit spectrum_pixel_acq...

    def show_matrixRGB(self): # basic usage c'est ça... espérons que ça marche vraiment
        plot = self.graph_rgb.ImageView()
        plot.autoRange(True)
        plot.show()
        plot.setImage(self.matrixRGB)

    def move_stage(self):
        pass
        #on pourrait créer une position avec avant et maintenant (en pixels) et avec la différence fois le pas (move by)
        #ou on prend la position initiale dans un attribut de la classe et on y additionne les tuples * pas à chaque fois
        #va manquer à importer le fichier de commnucation avec le stage (hardwareLibrary)

    def sweep(self, *args, **kwargs):
        self.countHeight = 0
        self.countWidth = 0
        self.countSpectrums = 0
        while self.isSweepThreadAlive:
            if self.countSpectrums < self.width*self.height:
                self.spectrum_pixel_acquisition()
                self.matrixData_replace()
                self.matrixRGB_replace()
                self.show_matrixRGB()
                if self.direction == "same":
                    if self.countWidth < self.width-1:
                        #wait for signal... (with a connect?)
                        self.countWidth += 1
                        self.move_stage()
                    elif self.countHeight < self.height and self.countWidth == self.width-1:
                        if self.countSpectrums < self.width*self.height-1:
                            # wait for signal...
                            self.countWidth = 0
                            self.countHeight += 1
                            self.move_stage()
                        else:
                            self.isSweepThreadAlive = False
                    else:
                        raise Exception(
                            'Somehow, the loop is trying to create more row or columns than asked on the GUI.')
                        #self.isSweepThreadAlive = False
                elif self.direction == "other":
                    if self.countWidth < self.width-1:
                        if self.countHeight % 2 == 0:
                            # wait for signal...
                            self.countWidth += 1
                            self.move_stage()
                        elif self.countHeight % 2 == 1:
                            # wait for signal...
                            self.countWidth -= 1
                            self.move_stage()
                    elif self.countHeight < self.height and self.countWidth == self.width-1:
                        if self.countSpectrums < self.width * self.height - 1:
                            # wait for signal...
                            self.countHeight += 1
                            self.move_stage()
                        else:
                            self.isSweepThreadAlive = False
                    else:
                        raise Exception(
                            'Somehow, the loop is trying to create more row or columns than asked on the GUI.')
                        # self.isSweepThreadAlive = False
                self.countSpectrums += 1
            else:
                self.isSweepThreadAlive = False

    #on veut donc activer acquisitionthread
    def begin(self):
        if not self.isSweepThreadAlive:
            try:
                self.disable_all_buttons()
                self.create_matrixData()
                self.sweepThread.start()
                self.saveThread.start()
                self.isSweepThreadAlive = True

            except Exception as e:
                self.spec = mock.MockSpectrometer()

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

    def save(self):
        pass
    #will use the dict from s_data_changed?

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