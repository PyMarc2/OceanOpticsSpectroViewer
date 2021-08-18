import numpy as np
import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from model.HyperSpectralImage import HyperSpectralImage

# HSI = HyperSpectralImage

skipTests = True

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

	def testSetWavelength(self):
		HSI = HyperSpectralImage()
		wavelength = [785, 786, 788, 789]
		HSI.setWavelength(wavelength)
		equality = np.equal(HSI.wavelength, np.array([785, 786, 788, 789]))
		result = equality.all()
		self.assertTrue(result)

	def testDeleteWavelength(self):
		HSI = HyperSpectralImage()
		self.assertEqual(len(HSI.wavelength), 0)
		wavelength =  [785, 786, 788, 789]
		HSI.setWavelength(wavelength)
		self.assertEqual(len(HSI.wavelength), 4)
		HSI.deleteWavelength()
		self.assertEqual(len(HSI.wavelength), 0)

	def testReturnWaveNumber(self):
		HSI = HyperSpectralImage()
		wavelength = [785, 786, 788, 789]
		HSI.setWavelength(wavelength)
		laserWaveLength = 785
		waveNumber = HSI.WaveNumber(laserWaveLength)
		equality = np.equal(waveNumber, np.array([0., 16., 48., 65.]))
		result = equality.all()
		self.assertTrue(result)

	def testAddSpectrum(self):
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

	def testDeleteSpectrum(self):
		HSI = HyperSpectralImage()
		x = 0
		y = 0
		spectrum = [1, 2, 3, 4]
		HSI.addSpectrum(x, y, spectrum)
		self.assertEqual(len(HSI.data), 1)
		HSI.deleteSpectrum()
		self.assertEqual(len(HSI.data), 0)

	def testReturnSpectrum(self):
		HSI = HyperSpectralImage()
		x = 0
		y = 0
		spectrum = [1, 2, 3, 4]
		HSI.addSpectrum(x, y, spectrum)
		returnSpectrum = HSI.spectrum(x, y, HSI.data)
		self.assertListEqual(returnSpectrum, spectrum)

	def testReturnSpectrumNone(self):
		HSI = HyperSpectralImage()
		returnSpectrum = HSI.spectrum(2, 100, HSI.data)
		self.assertIsNone(returnSpectrum)

	def testReturnWidthImage(self):
		HSI = HyperSpectralImage()
		HSI.addSpectrum(0, 0, [1, 2, 3])
		HSI.addSpectrum(0, 1, [4, 5, 6])
		HSI.addSpectrum(1, 0, [7, 8, 9])
		HSI.addSpectrum(1, 1, [10, 11, 12])
		HSI.addSpectrum(2, 0, [13, 14, 15])
		HSI.addSpectrum(2, 1, [16, 17, 18])

		width = HSI.widthImage(HSI.data)
		self.assertEqual(width, 3)

	def testReturnWidthImageWithNoData(self):
		HSI = HyperSpectralImage()
		width = HSI.widthImage(HSI.data)
		self.assertEqual(width, 0)

	def testReturnHeightImage(self):
		HSI = HyperSpectralImage()
		HSI.addSpectrum(0, 0, [1, 2, 3])
		HSI.addSpectrum(0, 1, [4, 5, 6])
		HSI.addSpectrum(1, 0, [7, 8, 9])
		HSI.addSpectrum(1, 1, [10, 11, 12])
		HSI.addSpectrum(2, 0, [13, 14, 15])
		HSI.addSpectrum(2, 1, [16, 17, 18])

		width = HSI.heightImage(HSI.data)
		self.assertEqual(width, 2)

	def testReturnHeightImageWithNoData(self):
		HSI = HyperSpectralImage()
		width = HSI.heightImage(HSI.data)
		self.assertEqual(width, 0)

	def testReturnSpectrumLen(self):
		HSI = HyperSpectralImage()
		x = 0
		y = 0
		spectrum = [1, 2, 3, 4]
		HSI.addSpectrum(x, y, spectrum)
		spectrumLen = HSI.spectrumLen(HSI.data)

	def testReturnSpectrumLenWithNoData(self):
		HSI = HyperSpectralImage()
		spectrumLen = HSI.spectrumLen(HSI.data)
		self.assertIsNone(spectrumLen)

	def testReturnSpectrumRange(self):
		HSI = HyperSpectralImage()
		wavelength = [785, 786, 788, 789]
		HSI.setWavelength(wavelength)
		spectrumRange = HSI.spectrumRange(HSI.wavelength)
		self.assertEqual(spectrumRange, 4)

	def testReturnSpectrumRangeNone(self):
		HSI = HyperSpectralImage()
		spectrumRange = HSI.spectrumRange(HSI.wavelength)
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

		matrix = HSI.matrixData(HSI.data)
		equality = np.equal(matrix, testMatrix)
		result = equality.all()
		self.assertTrue(result)

	def testMatrixDataWithNoData(self):
		HSI = HyperSpectralImage()
		matrix = HSI.matrixData(HSI.data)
		self.assertIsNone(matrix)

	def testMatrixRGB(self):
		HSI = HyperSpectralImage()
		HSI.addSpectrum(0, 0, [1, 2, 3, 4, 5, 6])
		HSI.addSpectrum(0, 1, [7, 8, 9, 10, 11, 12])
		HSI.addSpectrum(1, 0, [13, 14, 15, 16, 17, 18])
		HSI.addSpectrum(1, 1, [19, 20, 21, 22, 23, 24])
		matrix = HSI.matrixRGB(HSI.data, [0, 1/3, 1/3, 2/3, 2/3, 1])

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

		matrix = HSI.matrixRGB(HSI.data, [0, 1/3, 1/3, 2/3, 2/3, 1], globalMaximum=False)
		equality = np.equal(matrix, testMatrix)
		result = equality.all()
		self.assertTrue(result)

	def testMatrixRGBWithNoData(self):
		HSI = HyperSpectralImage()
		matrix = HSI.matrixRGB(HSI.data, [0, 1/3, 1/3, 2/3, 2/3, 1])
		self.assertIsNone(matrix)

	def testFindMaximum(self):
		HSI = HyperSpectralImage()
		HSI.addSpectrum(0, 0, [1, 2, 3, 4, 5, 6])
		HSI.addSpectrum(0, 1, [7, 8, 9, 10, 11, 12])
		HSI.addSpectrum(1, 0, [13, 14, 15, 16, 17, 18])
		HSI.addSpectrum(1, 1, [19, 20, 21, 22, 23, 24])


if __name__ == "__main__":
    unittest.main()