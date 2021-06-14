from PyQt5.QtWidgets import QWidget
from PyQt5.Qt import QPixmap
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5 import uic
import logging
import os

log = logging.getLogger(__name__)

microRamanViewUiPath = os.path.dirname(os.path.realpath(__file__)) + '{0}microRamanViewUi.ui'.format(os.sep)
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
        self.connect_widgets()

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
        pass

    def connect_signals(self):
        pass
