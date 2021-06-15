import numpy
from PyQt5.QtWidgets import QWidget
from PyQt5.Qt import QPixmap
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5 import uic
import os


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
        self.hauteur = 0
        self.largeur = 0
        self.step = 0
        self.ordre = 1
        self.direction = 'other'
        self.reset = False
        self.connect_widgets()
        self.exposureTime = 50
        self.integrationTime = 3000

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
        self.pb_sweepSame.clicked.connect(self.sweepSame)
        self.pb_sweepAlternate.clicked.connect(self.sweepOther)
        self.pb_reset.clicked.connect(self.resetAcq)
        self.pb_liveView.clicked.connect(self.begin)

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

    def sweepSame(self):
        self.direction = 'same'

    def sweepOther(self):
        self.direction = 'other'

    def resetAcq(self):
        self.reset = True
        #return True

    def setExposureTime(self):
        self.exposureTime = self.b_exposure.value()

    def setIntegrationTime(self):
        self.integrationTime = self.sb_acqTime.value()

    def begin(self):
        for i in range(100):
            self.pb_reset.clicked.connect(self.resetAcq)
            if not self.reset:
                self.pb_reset.clicked.connect(self.resetAcq)
                self.spinBox.setEnabled(False)
                self.spinBox_2.setEnabled(False)
                self.spinBox_3.setEnabled(False)
                self.comboBox.setEnabled(False)
                self.pb_sweepSame.setEnabled(False)
                self.pb_sweepAlternate.setEnabled(False)
                self.sb_exposure.setEnabled(False)
                self.sb_acqTime.setEnabled(False)
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