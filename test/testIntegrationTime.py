import unittest
import time
import acquisition as Int
import numpy as np


class TestIntegrationTime(unittest.TestCase):
    spec = Int.Integration()

    def testIntTimeOfBackground(self):
        tic = time.perf_counter()
        data = self.spec.acquire_background()
        toc = time.perf_counter()
        temps = round(toc - tic, 2)
        print(f'background = {temps}')
        print(f'background = {data}')
        self.assertIsInstance(data, np.ndarray)
        # self.assertTrue(temps == 12)

    def testIntTimeIsCorrect(self):
        tic = time.perf_counter()
        data = self.spec.spectrum_pixel_acquisition()
        toc = time.perf_counter()
        temps = round(toc-tic, 2)
        print(f'acq = {temps}')
        print(f'acq = {data}')
        self.assertIsInstance(data, np.ndarray)
        # self.assertTrue(temps == 11)

    def testTest(self):
        self.assertTrue(1)

    # def testIntTimeOfBackgroundSecondTime(self):
    #     tic = time.perf_counter()
    #     data = self.spec.acquireBackground()
    #     toc = time.perf_counter()
    #     temps = round(toc - tic, 2)
    #     print(f'background = {temps}')
    #     self.assertIsInstance(data, np.ndarray)
    #     # self.assertTrue(temps == 12)


if __name__ == "__main__":
    unittest.main()