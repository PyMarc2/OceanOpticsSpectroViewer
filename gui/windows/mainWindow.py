from gui.dialog.helpDialog import HelpDialog
from gui.views.paramsView import ParametersView
from gui.views.simulationView import SimulationView
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QVBoxLayout, QTabWidget, QAction
from PyQt5.QtCore import Qt, pyqtSlot
import logging
import os
from PyQt5 import uic

log = logging.getLogger(__name__)


MainWindowPath = os.path.dirname(os.path.realpath(__file__)) + '\\mainWindowUi.ui'
Ui_MainWindow, QtBaseClass = uic.loadUiType(MainWindowPath)


class MainWindow(QMainWindow, Ui_MainWindow):

    def __init__(self, model=None, controller=None):
        super(MainWindow, self).__init__()
        self.setAttribute(Qt.WA_AlwaysStackOnTop)
        self.setupUi(self)
        self.model = model

        self.create_views_and_dialogs()
        self.setup_window_tabs()
        self.setup_statusBar()
        self.setup_menuBar()
        self.connect_buttons()
        self.connect_signals()

    def setup_window_tabs(self):
        self.tabWidget = QTabWidget()
        self.setCentralWidget(self.tabWidget)
        self.tabWidget.addTab(self.simulationView, "Simulation")

    def setup_menuBar(self):
        self.helpAction = QAction(self)
        self.helpAction.setText("Help")
        self.menubar.addAction(self.helpAction)

    def setup_statusBar(self):
        self.statusbarMessage = QLabel()
        self.statusbar.addWidget(self.statusbarMessage)

    def create_views_and_dialogs(self):
        self.helpDialog = HelpDialog()
        self.simulationView = SimulationView(model=self.model)

    def connect_buttons(self):
        self.helpAction.triggered.connect(self.show_helpDialog)

    def connect_signals(self):
        self.helpDialog.s_windowClose.connect(lambda: self.setEnabled(True))

    def show_helpDialog(self):
        log.info('Help Dialog Opened')
        self.setEnabled(False)
        self.helpDialog.exec_()