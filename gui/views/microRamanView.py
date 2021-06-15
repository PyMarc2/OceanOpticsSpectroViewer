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

    def setExposureTime(self):
        self.exposureTime = self.b_exposure.value()

    def setIntegrationTime(self):
        self.integrationTime = self.sb_acqTime.value()

    def begin(self):
        """
        while self.reset is False:
            self.spinBox.setEnabled(True)
            self.spinBox_2.setEnabled(True)
            self.spinBox_3.setEnabled(True)
            self.comboBox.setEnabled(True)
            self.pb_sweepSame.setEnabled(True)
            self.pb_sweepAlternate.setEnabled(True)
            self.sb_exposure.setEnabled(True)
            self.sb_acqTime.setEnabled(True)
        """
