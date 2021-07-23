import numpy as np
import time

# MockSpectrometer() = self.spec


class Integration:
    def __init__(self):
        self.waves = MockSpectrometer().wavelengths()[2:]
        self.expositionCounter = 0
        self.exposureTime = 1000
        self.integrationTimeAcq = 3000
        self.integrationCountAcq = 0
        self.movingIntegrationData = None

    # SETTINGS
    def set_exposure_time(self, time_in_ms=None, update=True):
        if time_in_ms is not None:
            expositionTime = time_in_ms

        else:
            expositionTime = self.exposureTime

        MockSpectrometer().integration_time_micros(expositionTime * 1000)
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
            self.sb_acqTime.setStyleSheet('color: red')

        if self.integrationTimeAcqRemainder_ms > 3:
            self.movingIntegrationData = RingBuffer(size_max=self.integrationCountAcq+1)
            self.changeLastExposition = 1

        else:
            self.movingIntegrationData = RingBuffer(size_max=self.integrationCountAcq)
            self.changeLastExposition = 0

    # ACQUISITION
    def spectrum_pixel_acquisition(self):
        self.dataLen = len(self.waves)
        self.dataSep = (max(self.waves) - min(self.waves)) / len(self.waves)

        self.liveAcquisitionData = self.read_data_live().tolist()

        self.integrate_data()

        if not self.isAcquiringBackground:
            self.dataPixel = np.mean(np.array(self.movingIntegrationData()), 0)
        else:
            self.backgroundData = np.mean(np.array(self.movingIntegrationData()), 0)

    def acquire_background(self):
        self.isAcquiringBackground = True
        if MockSpectrometer() is None:
            self.connect_detection()

        if self.folderPath == "":
            self.error_folder_name()

        else:
            try:
                self.disable_all_buttons()
                self.set_integration_time()
                self.spectrum_pixel_acquisition()
                self.start_save(data=self.backgroundData)
                self.enable_all_buttons()

            except Exception as e:
                print(f"Error in acquire_background: {e}")

        self.isAcquiringBackground = False

    def integrate_data(self):
        self.isAcquisitionDone = False
        if self.expositionCounter < self.integrationCountAcq - 1:
            self.movingIntegrationData.append(self.liveAcquisitionData)
            self.expositionCounter += 1

        elif self.expositionCounter == self.integrationCountAcq - 1:
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
        return MockSpectrometer().intensities()[2:]


class MockSpectrometer:
    def __init__(self):
        self.exposureTime = 3000
        self.shutter = 0.2
        self.backgroundIntensity = 0.005
        self.noise = 0.01

        self._background = background_spectrum()
        self._source = halogen_spectrum()
        # todo: move bg and source to spectrum object
        # todo: calibration offset?

    def integration_time_micros(self, integration_time_micros: int):
        self.exposureTime = integration_time_micros

    def wavelengths(self) -> np.ndarray:
        return np.linspace(339.24, 1022.28, 2048)

    def intensities(self) -> np.ndarray:
        t = time.time()
        background = self._background * self.backgroundIntensity * self.exposureFactor
        source = self._source * self.exposureFactor * self.shutterFactor
        noise = np.random.uniform(0, self.noise, 2048)
        out = np.clip((background + source + noise) * 4095, 0, 4095)

        delta = time.time() - t
        sleepTime = self.exposureTime / 1000000 - delta
        if sleepTime > 0:
            time.sleep(sleepTime)
        return out

    @property
    def exposureFactor(self):
        return self.exposureTime / 3000

    @property
    def shutterFactor(self):
        return self.shutter ** 2 / 0.5


def gaussian(x, mu, sig):
    return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))


def halogen_spectrum():
    x = np.linspace(339.24, 1022.28, 2048)
    return gaussian(x, mu=600, sig=100) * 0.7 + gaussian(x, mu=700, sig=70) * 0.3


def background_spectrum():
    x = np.linspace(339.24, 1022.28, 2048)
    return gaussian(x, mu=550, sig=5) * 1 + gaussian(x, mu=610, sig=8) * 0.7 + \
           gaussian(x, mu=480, sig=15) * 0.2 + gaussian(x, mu=550, sig=200) * 0.1


# On essaye de lancer l'acquisition

Integration().spectrum_pixel_acquisition()

