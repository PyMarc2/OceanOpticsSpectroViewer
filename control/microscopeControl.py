from tools.CircularList import RingBuffer
from model.microscopeDevice import Model
import numpy as np


class MicroscopeControl:
    def __init__(self):
        self.acq = Model()
        self.appControl = None

    # TODO find the real and updated links for those functions in the microscopeDevice file
    # SETTINGS
    # def setWidth(self, width):
    #     self.acq.setWidth(width)
    #
    # def setHeight(self, height):
    #     self.acq.setHeight(height)
    #
    # def setStep(self, step):
    #     self.acq.setStep(step)
    #
    # def setStepMeasureUnit(self, unit):
    #     self.acq.setStepMeasureUnit(unit)
    #
    # def setExposureTime(self, exposition):
    #     self.setExposureTime(exposition)
    #
    # def setIntegrationTime(self, integration):
    #     self.setIntegrationTime(integration)
    #
    # def setDirectionToDefault(self):
    #     self.acq.setDirectionToDefault()
    #
    # def setDirectionToZigzag(self):
    #     self.acq.setDirectionToZigzag()
    #
    # def getStage(self):
    #     if self.acq.stage is None:
    #         return False
    #     return True
    #
    # def getSpectro(self):
    #     if self.acq.spec is None:
    #         return False
    #     return True
    #
    # def connectDetection(self, index):
    #     self.connectSpectro(index)
    #     waves = self.spec.wavelengths()[2:]
    #     return waves
    #
    # def connectStage(self, index):
    #     self.connectStage(index)
    #     self.positionSutter = self.stage.position()

    # TODO you will need those in your appControl
    def getStageList(self):
        return self.acq.listStageDevices()

    def getSpecList(self):
        return self.acq.listSpecDevices()
