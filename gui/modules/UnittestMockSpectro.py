import numpy as np
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from mockSpectrometer import MockSpectrometer

# HSI = HyperSpectralImage

skipTests = True

class TestMockSpectro(unittest.TestCase):
	def testImportMS(self):
		self.assertIsNotNone(MockSpectrometer)

	def testCreateMSInstance(self):
		MS = MockSpectrometer()
		self.assertIsNotNone(MS)

	def testIntegrationTime(self):
		MS = MockSpectrometer()
		MS.integration_time_micros(50)
		validate = MS.exposureTime
		self.assertEqual(50, validate)

	def testWavelength(self):
		MS = MockSpectrometer()
		waves = MS.wavelengths()
		self.assertEqual(len(waves), 2048)

	def testIntensities(self):
		MS = MockSpectrometer()
		waves = MS.intensities()
		self.assertEqual(len(waves), 2048)





if __name__ == "__main__":
    unittest.main()