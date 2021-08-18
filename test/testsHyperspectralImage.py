from typing import NamedTuple
import numpy as np
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from model.HyperSpectralImage import HyperSpectralImage

# HSI = HyperSpectralImage

skipTests = True
# @unittest.skipIf(skipTests, "")

class ColorValues(NamedTuple):
    lowRed: int = None
    highRed: int = None
    lowGreen: int = None
    highGreen: int = None
    lowBlue: int = None
    highBlue: int = None

class TestHyperSpectralImage(unittest.TestCase):

	def testImportHSI(self):
		self.assertIsNotNone(HyperSpectralImage)

	def testCreateHSIInstance(self):
		HSI = HyperSpectralImage()
		self.assertIsNotNone(HSI)

	def testDefaultDataIsEmpty(self):
		HSI = HyperSpectralImage()
		self.assertEqual(len(HSI.data), 0)

	def testDefaultWavelenthIsEmpty(self):
		HSI = HyperSpectralImage()
		self.assertEqual(len(HSI.wavelength), 0)

	def testDefaultBackgroundIsEmpty(self):
		HSI = HyperSpectralImage()
		self.assertEqual(len(HSI.background), 0)


	# Publics functions

	def testAddSpectrum(self): # addSpectrum(self, x, y, spectrum):
		HSI = HyperSpectralImage()
		x = 0
		y = 0
		spectrum = [1, 2, 3, 4]
		HSI.addSpectrum(x, y, spectrum)
		self.assertEqual(len(HSI.data), 1)
		self.assertEqual(len(HSI.data[0]), 3)
		self.assertIsInstance(HSI.data[0].x, int)
		self.assertIsInstance(HSI.data[0].y, int)
		self.assertEqual(len(HSI.data[0].spectrum), 4)

	def testAddSpectrumTypeErrorX(self): # addSpectrum(self, x, y, spectrum):
		pass

	def testAddSpectrumTypeErrorY(self): # addSpectrum(self, x, y, spectrum):
		pass

	def testAddSpectrumTypeErrorSpectrum(self): # addSpectrum(self, x, y, spectrum):
		pass


	def testDeleteSpectra(self): # deleteSpectra(self):
		HSI = HyperSpectralImage()
		x = 0
		y = 0
		spectrum = [1, 2, 3, 4]
		HSI.addSpectrum(x, y, spectrum)
		self.assertEqual(len(HSI.data), 1)
		HSI.deleteSpectra()
		self.assertEqual(len(HSI.data), 0)

	def testReturnSpectrum(self): # spectrum(self, x, y, subtractBackground=False):
		HSI = HyperSpectralImage()
		x = 0
		y = 0
		spectrum = [1, 2, 3, 4]
		HSI.addSpectrum(x, y, spectrum)
		returnSpectrum = HSI.spectrum(x, y)
		spectrum = np.array(spectrum)
		equality = np.equal(returnSpectrum, spectrum)
		result = equality.all()
		self.assertTrue(result)

	def testReturnSpectrumNone(self): # spectrum(self, x, y, subtractBackground=False):
		HSI = HyperSpectralImage()
		returnSpectrum = HSI.spectrum(2, 100)
		self.assertIsNone(returnSpectrum)

	def testReturnSpectrumTypeErrorX(self): # spectrum(self, x, y, subtractBackground=False):
		pass

	def testReturnSpectrumTypeErrorY(self): # spectrum(self, x, y, subtractBackground=False):
		pass

	def testReturnSpectrumTypeErrorSubtractBackground(self): # spectrum(self, x, y, subtractBackground=False):
		pass


	def testSetBackground(self): # setBackground(self, background):
		pass

	def testSetBackgroundTypeError(self): # setBackground(self, background):
		pass

	def testDeleteBackground(self): # deleteBackground(self):
		pass


	def testSetWavelength(self): # setWavelength(self, wavelength):
		HSI = HyperSpectralImage()
		wavelength = [785, 786, 788, 789]
		HSI.setWavelength(wavelength)
		equality = np.equal(HSI.wavelength, np.array([785, 786, 788, 789]))
		result = equality.all()
		self.assertTrue(result)

	def testSetWavelengthTypeError(self): # setWavelength(self, wavelength):
		pass

	def testDeleteWavelength(self): # deleteWavelength(self):
		HSI = HyperSpectralImage()
		self.assertEqual(len(HSI.wavelength), 0)
		wavelength =  [785, 786, 788, 789]
		HSI.setWavelength(wavelength)
		self.assertEqual(len(HSI.wavelength), 4)
		HSI.deleteWavelength()
		self.assertEqual(len(HSI.wavelength), 0)

	def testReturnWaveNumber(self): # def waveNumber(self):
		HSI = HyperSpectralImage()
		wavelength = [785, 786, 788, 789]
		laserWaveLength = 785
		HSI.setWavelength(wavelength)
		HSI.setLaserWavelength(laserWaveLength)
		waveNumber = HSI.waveNumber()
		equality = np.equal(waveNumber, np.array([0., 16., 48., 65.]))
		result = equality.all()
		self.assertTrue(result)

	def testReturnWaveNumberErrorLaser(self): # def waveNumber(self):
		pass

	def testReturnWaveNumberErrorWavelength(self): # def waveNumber(self):
		pass

	def testSetLaserWavelength(self): # setLaserWavelength(self, laser):
		pass

	def testSetLaserWavelengthTypeError(self): # setLaserWavelength(self, laser):
		pass








	def testReturnWidthImage(self):
		HSI = HyperSpectralImage()
		HSI.addSpectrum(0, 0, [1, 2, 3])
		HSI.addSpectrum(0, 1, [4, 5, 6])
		HSI.addSpectrum(1, 0, [7, 8, 9])
		HSI.addSpectrum(1, 1, [10, 11, 12])
		HSI.addSpectrum(2, 0, [13, 14, 15])
		HSI.addSpectrum(2, 1, [16, 17, 18])

		width = HSI.widthImage()
		self.assertEqual(width, 3)

	def testReturnWidthImageWithNoData(self):
		HSI = HyperSpectralImage()
		width = HSI.widthImage()
		self.assertEqual(width, 0)

	def testReturnHeightImage(self):
		HSI = HyperSpectralImage()
		HSI.addSpectrum(0, 0, [1, 2, 3])
		HSI.addSpectrum(0, 1, [4, 5, 6])
		HSI.addSpectrum(1, 0, [7, 8, 9])
		HSI.addSpectrum(1, 1, [10, 11, 12])
		HSI.addSpectrum(2, 0, [13, 14, 15])
		HSI.addSpectrum(2, 1, [16, 17, 18])

		width = HSI.heightImage()
		self.assertEqual(width, 2)

	def testReturnHeightImageWithNoData(self):
		HSI = HyperSpectralImage()
		width = HSI.heightImage()
		self.assertEqual(width, 0)

	def testReturnSpectrumLen(self):
		HSI = HyperSpectralImage()
		x = 0
		y = 0
		spectrum = [1, 2, 3, 4]
		HSI.addSpectrum(x, y, spectrum)
		spectrumLen = HSI.spectrumLen()

	def testReturnSpectrumLenWithNoData(self):
		HSI = HyperSpectralImage()
		spectrumLen = HSI.spectrumLen()
		self.assertIsNone(spectrumLen)

	def testReturnSpectrumRange(self):
		HSI = HyperSpectralImage()
		wavelength = [785, 786, 788, 789]
		HSI.setWavelength(wavelength)
		spectrumRange = HSI.spectrumRange()
		self.assertEqual(spectrumRange, 4)


	def testReturnSpectrumRangeNone(self):
		HSI = HyperSpectralImage()
		spectrumRange = HSI.spectrumRange()
		self.assertIsNone(spectrumRange)

	def testMatrixData(self):
		HSI = HyperSpectralImage()
		HSI.addSpectrum(0, 0, [1, 2, 3])
		HSI.addSpectrum(0, 1, [4, 5, 6])
		HSI.addSpectrum(1, 0, [7, 8, 9])
		HSI.addSpectrum(1, 1, [10, 11, 12])
		HSI.addSpectrum(2, 0, [13, 14, 15])
		HSI.addSpectrum(2, 1, [16, 17, 18])

		testMatrix = np.zeros((2, 3, 3))
		testMatrix[0][0] = np.array([1, 2, 3])
		testMatrix[1][0] = np.array([4, 5, 6])
		testMatrix[0][1] = np.array([7, 8, 9])
		testMatrix[1][1] = np.array([10, 11, 12])
		testMatrix[0][2] = np.array([13, 14, 15])
		testMatrix[1][2] = np.array([16, 17, 18])

		matrix = HSI.matrixData()
		equality = np.equal(matrix, testMatrix)
		result = equality.all()
		self.assertTrue(result)


	def testMatrixDataWithNoData(self):
		HSI = HyperSpectralImage()
		matrix = HSI.matrixData()
		self.assertIsNone(matrix)

	def testMatrixRGB(self):
		HSI = HyperSpectralImage()
		HSI.addSpectrum(0, 0, [1, 2, 3, 4, 5, 6])
		HSI.addSpectrum(0, 1, [7, 8, 9, 10, 11, 12])
		HSI.addSpectrum(1, 0, [13, 14, 15, 16, 17, 18])
		HSI.addSpectrum(1, 1, [19, 20, 21, 22, 23, 24])
		colorValues = ColorValues(0, 1/3, 1/3, 2/3, 2/3, 1)
		matrix = HSI.matrixRGB(colorValues)

		testMatrix = np.zeros((2, 2, 3))
		testMatrix[0][0] = np.array([3, 7, 11])
		testMatrix[1][0] = np.array([15, 19, 23])
		testMatrix[0][1] = np.array([27, 31, 35])
		testMatrix[1][1] = np.array([39, 43, 47])
		testMatrix = (testMatrix / np.max(testMatrix)) * 255
		testMatrix = testMatrix.round(0)

		equality = np.equal(matrix, testMatrix)
		result = equality.all()
		self.assertTrue(result)


	def testMatrixRGBGlobalMaximumFalse(self):
		HSI = HyperSpectralImage()
		HSI.addSpectrum(0, 0, [1, 2, 3, 4, 5, 6])
		HSI.addSpectrum(0, 1, [7, 8, 9, 10, 11, 12])
		HSI.addSpectrum(1, 0, [13, 14, 15, 16, 17, 18])
		HSI.addSpectrum(1, 1, [19, 20, 21, 22, 23, 24])

		testMatrix = np.zeros((2, 2, 3))
		testMatrix[0][0] = np.array([3, 7, 11])
		testMatrix[1][0] = np.array([15, 19, 23])
		testMatrix[0][1] = np.array([27, 31, 35])
		testMatrix[1][1] = np.array([39, 43, 47])
		maxima = testMatrix.max(axis=2)
		maxima = np.dstack((maxima,) * 3)
		testMatrix /= maxima
		testMatrix *= 255
		testMatrix = testMatrix.round(0)

		colorValues = ColorValues(0, 1/3, 1/3, 2/3, 2/3, 1)

		matrix = HSI.matrixRGB(colorValues, globalMaximum=False)
		equality = np.equal(matrix, testMatrix)
		result = equality.all()
		self.assertTrue(result)

	def testMatrixRGBWithNoData(self):
		HSI = HyperSpectralImage()
		colorValues = ColorValues(0, 1/3, 1/3, 2/3, 2/3, 1)
		matrix = HSI.matrixRGB(colorValues)
		self.assertIsNone(matrix)

	def testFindMaximum(self):
		HSI = HyperSpectralImage()
		HSI.addSpectrum(0, 0, [1, 2, 3, 4, 5, 6])
		HSI.addSpectrum(0, 1, [7, 8, 9, 10, 11, 12])
		HSI.addSpectrum(1, 0, [13, 14, 15, 16, 17, 18])
		HSI.addSpectrum(1, 1, [19, 20, 21, 22, 23, 24])


if __name__ == "__main__":
    unittest.main()