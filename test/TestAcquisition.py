import numpy as np
from tools.CircularList import RingBuffer
from gui.modules import mockSpectrometer as Mock


class Integration:
    def __init__(self):
        self.waves = Mock.MockSpectrometer().wavelengths()[2:]
        self.spec = Mock.MockSpectrometer()
        self.expositionCounter = 0
        self.exposureTime = 1000
        self.integrationTimeAcq = 5000
        self.integrationCountAcq = 0
        self.movingIntegrationData = None
        self.isAcquiringBackground = False
        self.dataPixel = []
        self.liveAcquisitionData = []
        self.integrationTimeAcqRemainder_ms = 0
        self.isAcquisitionDone = False
        self.changeLastExposition = 0
        self.dataSep = 0
        self.dataLen = 0
        self.backgroundData = []

    # SETTINGS
    def set_exposure_time(self, time_in_ms=None, update=True):
        if time_in_ms is not None:
            expositionTime = time_in_ms

        else:
            expositionTime = self.exposureTime

        self.spec.integration_time_micros(expositionTime * 1000)
        if update:
            self.set_integration_time()

    def set_integration_time(self):
        try:
            if self.integrationTimeAcq >= self.exposureTime:
                self.integrationCountAcq = self.integrationTimeAcq // self.exposureTime
                self.integrationTimeAcqRemainder_ms = self.integrationTimeAcq - (
                        self.integrationCountAcq * self.exposureTime)

            else:
                self.integrationCountAcq = 1

        except ValueError:
            print('nope, wrong value of integration:D')

        if self.integrationTimeAcqRemainder_ms > 3:
            self.movingIntegrationData = RingBuffer(size_max=self.integrationCountAcq + 1)
            self.changeLastExposition = 1

        else:
            self.movingIntegrationData = RingBuffer(size_max=self.integrationCountAcq)
            self.changeLastExposition = 0

    # ACQUISITION
    def spectrum_pixel_acquisition(self):
        self.set_exposure_time()
        self.isAcquisitionDone = False

        self.waves = self.spec.wavelengths()[2:]
        self.dataLen = len(self.waves)
        self.dataSep = (max(self.waves) - min(self.waves)) / len(self.waves)

        # counter = 0
        while not self.isAcquisitionDone:
            self.liveAcquisitionData = self.read_data_live().tolist()
            self.integrate_data()
            self.dataPixel = np.mean(np.array(self.movingIntegrationData()), 0)
            # counter += 1
        # print(counter)

        return self.dataPixel

    def acquire_background(self):
        self.isAcquiringBackground = True
        self.backgroundData = self.spectrum_pixel_acquisition()
        return self.backgroundData

    def integrate_data(self):
        self.isAcquisitionDone = False
        if self.expositionCounter < self.integrationCountAcq - 2:
            self.movingIntegrationData.append(self.liveAcquisitionData)
            self.expositionCounter += 1

        elif self.expositionCounter == self.integrationCountAcq - 2:
            self.movingIntegrationData.append(self.liveAcquisitionData)
            self.expositionCounter += 1
            if self.changeLastExposition:
                self.set_exposure_time(self.integrationTimeAcqRemainder_ms, update=False)

        else:
            self.set_exposure_time(update=False)
            self.movingIntegrationData.append(self.liveAcquisitionData)
            self.isAcquisitionDone = True
            self.expositionCounter = 0

    def read_data_live(self):
        return self.spec.intensities()[2:]


# if __name__ == "__main__":
#     tic = time.perf_counter()
#     print(Integration().spectrumPixelAcquisition())
#     toc = time.perf_counter()
#     print(toc-tic)
