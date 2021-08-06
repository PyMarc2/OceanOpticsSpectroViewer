from typing import NamedTuple
import seabreeze.spectrometers as sb
import hardwarelibrary
import hardwarelibrary.motion.sutterdevice as sutter
from gui.modules import mockSpectrometer as Mock


class DataPoint(NamedTuple):
    x: int = None
    y: int = None
    spectrum: list = None


class Background(NamedTuple):
    title: str = 'background'
    spectrum: list = None


class Model:
    def __init__(self):
        self.stage = None
        self.spec = None

        self.width: int = 2
        self.height: int = 2
        self.step: int = 1
        self.stepMeasureUnit: float = 10**3
        self.exposureTime: int = 500
        self.integrationTime = 3000
        self.direction = "same"

        self.dataPixel: list = None

    def createDataPixelTuple(self, x: int, y: int, spectrum: list):
        return DataTuple(x, y, spectrum)

    def createBackgroundTuple(self, spectrum):
        BackgroundTuple(spectrum=spectrum)

    def setWidth(self, width):
        self.width = width

    def setHeight(self, height):
        self.height = height

    def setStep(self, step):
        self.step = step

    def setStepMeasureUnit(self, unit):
        if unit == 'mm':
            self.stepMeasureUnit = 10**3

        elif unit == 'um':
            self.stepMeasureUnit = 1

        elif unit == 'nm':
            self.stepMeasureUnit = 10**(-3)

        else:
            print('What the hell is going on?!')

    def setExposureTime(self, exposition):
        self.exposureTime = exposition

    def setIntegrationTime(self, integration):
        self.integrationTime = integration

    def setDirectionToDefault(self):
        self.direction = "same"

    def setDirectionToZigzag(self):
        self.direction = "other"
