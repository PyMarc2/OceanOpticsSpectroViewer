from typing import NamedTuple
import seabreeze.spectrometers as sb
import hardwarelibrary
import hardwarelibrary.motion.sutterdevice as sutter
from gui.modules import mockSpectrometer as Mock


class DataTuple(NamedTuple):
    x: int = None
    y: int = None
    spectrum: list = None


class BackgroundTuple(NamedTuple):
    title: str = 'background'
    spectrum: list = None


class Model:
    def __init__(self):
        self.stageDevices = []  # find list from hardware...  # TODO
        self.setStageDevicesList()
        self.stageLink = self.stageDevices[0]
        self.stage = None

        self.specDevices = []
        self.setSpecDevicesList()
        self.spectroLink = self.specDevices[0]
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

    def listStageDevices(self) -> list:
        self.setStageDevicesList()
        devices = []
        for stage in self.stageDevices:
            devices.append(str(stage))
        return devices

    def setStageDevicesList(self):
        self.stageDevices = []  # find list from hardware... # TODO
        self.stageDevices.insert(0, "Debug")
        self.stageDevices.append("real Sutter")

    def connectStage(self, index):
        self.stageLink = self.stageDevices[index]
        if self.stageLink == "Debug":
            self.stage = sutter.SutterDevice(serialNumber="debug")
            self.stage.doInitializeDevice()
        else:
            # TODO will update with list provided by sepo.SerialPort.matchPorts(idVendor=4930, idProduct=1)...
            self.stage = sutter.SutterDevice()
            self.stage.doInitializeDevice()
        if self.stage is None:
            raise Exception('The sutter is not connected!')

    def listSpecDevices(self) -> list:
        self.setSpecDevicesList()
        devices = []
        for spec in self.specDevices:
            devices.append(str(spec))
        return devices

    def setSpecDevicesList(self):
        self.specDevices = sb.list_devices()
        self.specDevices.insert(0, "MockSpectrometer")

    def connectSpectro(self, index):
        self.spectroLink = self.specDevices[index]
        if self.spectroLink == "MockSpectrometer":
            self.spec = Mock.MockSpectrometer()
        else:
            self.spec = sb.Spectrometer(self.spectroLink)
        if self.spec is None:
            raise Exception('The spectrometer is not connected!')

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
