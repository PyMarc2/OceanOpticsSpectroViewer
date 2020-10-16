import logging
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QSettings
import os


log = logging.getLogger(__name__)


class MainModel(QObject):

    def __init__(self):
        super(MainModel, self).__init__()

