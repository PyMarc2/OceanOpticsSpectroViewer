import numpy as np
import time
import random


class MockSpectrometer:
    def __init__(self):
        self.exposureTime = 3000
        self.shutter = 0.2
        self.backgroundIntensity = 0.005
        self.noise = 0.01

        self._background = background_spectrum()
        self._source = "halogen"
        # todo: move bg and source to spectrum object
        # todo: calibration offset?

    def integration_time_micros(self, integration_time_micros: int):
        self.exposureTime = integration_time_micros

    def wavelengths(self) -> np.ndarray:
        return np.linspace(784.48, 1029.63, 1042)

    def intensities(self) -> np.ndarray:
        if self._source == "random":
            source_spectrum = random_spectrum()
        else:
            source_spectrum = halogen_spectrum()

        t = time.time()
        background = self._background * self.backgroundIntensity * self.exposureFactor
        source = source_spectrum * self.exposureFactor * self.shutterFactor
        noise = np.random.uniform(0, self.noise, 1042)
        out = np.clip((background + source + noise) * 4095, 0, 8192)

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
    x = np.linspace(784.48, 1029.63, 1042)
    return gaussian(x, mu=900, sig=20) * 0.7 + gaussian(x, mu=930, sig=5) * 0.3

def random_spectrum():
    x = np.linspace(784.48, 1029.63, 1042)
    spectrum = random.randint(1, 6)
    if spectrum == 1:
        y = gaussian(x, mu=900, sig=20) * 0.7 + gaussian(x, mu=950, sig=5) * 0.3 + gaussian(x, mu=820, sig=5) * 0.1
    elif spectrum == 2:
        y = gaussian(x, mu=900, sig=20) * 0.7 + gaussian(x, mu=820, sig=5) * 0.3 + gaussian(x, mu=950, sig=5) * 0.1 
    elif spectrum == 3:
        y = gaussian(x, mu=950, sig=20) * 0.7 + gaussian(x, mu=820, sig=5) * 0.3 + gaussian(x, mu=900, sig=5) * 0.1
    elif spectrum == 4:
        y = gaussian(x, mu=950, sig=20) * 0.7 + gaussian(x, mu=900, sig=5) * 0.3 + gaussian(x, mu=820, sig=5) * 0.1
    elif spectrum == 5:
        y = gaussian(x, mu=820, sig=20) * 0.7 + gaussian(x, mu=900, sig=5) * 0.3 + gaussian(x, mu=950, sig=5) * 0.1
    elif spectrum == 6:
        y = gaussian(x, mu=820, sig=20) * 0.7 + gaussian(x, mu=950, sig=5) * 0.3 + gaussian(x, mu=900, sig=5) * 0.1
    return y

def background_spectrum():
    x = np.linspace(784.48, 1029.63, 1042)
    return gaussian(x, mu=870, sig=1) * 1 + gaussian(x, mu=960, sig=60) * 0.7 + \
           gaussian(x, mu=780, sig=15) * 0.2 + gaussian(x, mu=850, sig=200) * 0.1
