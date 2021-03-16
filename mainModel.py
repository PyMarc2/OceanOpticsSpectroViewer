import logging
from PyQt5.QtCore import QObject, pyqtSlot, pyqtSignal, QSettings
import os


log = logging.getLogger(__name__)


class MainModel(QObject):
    s_mouse_graph_position = pyqtSignal()

    def __init__(self):
        super(MainModel, self).__init__()
        self._mouse_x = 0
        self._mouse_y = 0

    @property
    def exposureTime(self):
        return

    @exposureTime.setter
    def exposureTime(self, value):
        pass

    @property
    def mouseX(self):
        return self._mouse_x

    @property
    def mouseY(self):
        return self._mouse_y

    @property
    def mousePosition(self):
        return [self._mouse_x, self._mouse_y]

    @mousePosition.setter
    def mousePosition(self, value):
        self. _mouse_x = value[0]
        self._mouse_y = value[1]
        self.s_mouse_graph_position.emit()

