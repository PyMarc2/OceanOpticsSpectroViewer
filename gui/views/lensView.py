from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal
from PyQt5 import uic
import logging
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

    def connect_widgets(self):
        pass

    def connect_signals(self):
        pass
