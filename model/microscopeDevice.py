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
    def __init__(self, stage, detection):
        self.spec = detection
        self.stage = stage
        self._stagePosition = None
        # self.resetStagePosition()

        self._width: int = 2
        self._height: int = 2
        self._step: int = 1
        self._stepMeasureUnit: float = 10**3
        self._exposureTime: int = 500
        self._integrationTime = 3000
        self._direction = "same"

        self.waves: list = []
        self.dataPoint: list = []
        self.dataMap: list = []
        self.background: list = []

    @property
    def stagePosition(self):
        return self._stagePosition

    def resetStagePosition(self):
        self._stagePosition = self.stage.position()

    def createDataPoint(self, x: int, y: int, spectrum: list):
        return DataPoint(x, y, spectrum)

    def createBackground(self, spectrum):
        Background(spectrum=spectrum)

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, width):
        # TODO maybe create function with those conditions to make sure they are still being uphold at the start map
        # they are basically the same for every setup sooo... they just have to be called before
        if width * self._step * self._stepMeasureUnit + self._stagePosition[0] > self.stage.xMaxLimit:  # TODO is it in native steps or in microns??
            raise ValueError("The stage does not allow such an important range of motion.")
        if width <= 0:
            raise ValueError("Images will be mapped strictly with positive coordinates.")
        self._width = width

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height):
        self._height = height

    @property
    def step(self):
        return self._step

    @step.setter
    def step(self, step):
        self._step = step

    @property
    def stepMeasureUnit(self):
        return self._stepMeasureUnit

    @stepMeasureUnit.setter
    def stepMeasureUnit(self, unit):
        if unit == 'mm':
            self._stepMeasureUnit = 10**3

        elif unit == 'um':
            self._stepMeasureUnit = 1

        elif unit == 'nm':
            self._stepMeasureUnit = 10**(-3)

    @property
    def exposureTime(self):
        return self._exposureTime

    @exposureTime.setter
    def exposureTime(self, exposition):
        self._exposureTime = exposition

    @property
    def integrationTime(self):
        return self._integrationTime

    @integrationTime.setter
    def integrationTime(self, integration):
        self._integrationTime = integration

    def setDirectionToDefault(self):
        self.direction = "same"

    def setDirectionToZigzag(self):
        self.direction = "other"
