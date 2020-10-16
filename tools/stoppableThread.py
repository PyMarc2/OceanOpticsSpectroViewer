from PyQt5.QtCore import QThread, QMutex
import threading


class QStoppableThread(QThread):
    def __init__(self, mutex=None):
        super(QStoppableThread, self).__init__()
        self.mutex = threading.Lock()

