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
		HSI = HyperSpectralImage(createTempFolder=False)
		self.assertIsNotNone(HSI)

	def testDefaultDataIsEmpty(self):
		HSI = HyperSpectralImage(createTempFolder=False)
		self.assertEqual(len(HSI.spectralPoints), 0)

	def testDefaultWavelenthIsEmpty(self):
		HSI = HyperSpectralImage(createTempFolder=False)
		self.assertEqual(len(HSI.wavelength), 0)

	def testDefaultBackgroundIsEmpty(self):
		HSI = HyperSpectralImage(createTempFolder=False)
		self.assertEqual(len(HSI.background), 0)

	# Publics functions

	def testAddSpectrum(self): # addSpectrum(self, x, y, spectrum):
		HSI = HyperSpectralImage(createTempFolder=False)
		x = 0
		y = 0
		spectrum = [1, 2, 3, 4]
		HSI.addSpectrum(x, y, spectrum, autoSave=False)
		self.assertEqual(len(HSI.spectralPoints), 1)
		self.assertEqual(len(HSI.spectralPoints[0]), 3)
		self.assertIsInstance(HSI.spectralPoints[0].x, int)
		self.assertIsInstance(HSI.spectralPoints[0].y, int)
		self.assertEqual(len(HSI.spectralPoints[0].spectrum), 4)

	def testAddSpectrumTypeErrorX(self): # addSpectrum(self, x, y, spectrum):
		HSI = HyperSpectralImage(createTempFolder=False)
		x = 0.5
		y = 0
		spectrum = [1, 2, 3, 4]
		try:
			HSI.addSpectrum(x, y, spectrum)
		except Exception as e:
			e = str(e)
			self.assertMultiLineEqual(e, "x argument is not int.")
			self.assertEqual(len(HSI.spectralPoints), 0)

	def testAddSpectrumTypeErrorY(self): # addSpectrum(self, x, y, spectrum):
		HSI = HyperSpectralImage(createTempFolder=False)
		x = 0
		y = 0.5
		spectrum = [1, 2, 3, 4]
		try:
			HSI.addSpectrum(x, y, spectrum)
		except Exception as e:
			e = str(e)
			self.assertMultiLineEqual(e, "y argument is not int.")
			self.assertEqual(len(HSI.spectralPoints), 0)

	def testAddSpectrumTypeErrorSpectrum(self): # addSpectrum(self, x, y, spectrum):
		HSI = HyperSpectralImage(createTempFolder=False)
		x = 0
		y = 0
		spectrum = (1,2,3,4)
		try:
			HSI.addSpectrum(x, y, spectrum)
		except Exception as e:
			e = str(e)
			self.assertMultiLineEqual(e, "spectrum argument is not a list or numpy.ndarray.")
			self.assertEqual(len(HSI.spectralPoints), 0)


	def testDeleteSpectra(self): # deleteSpectra(self):
		HSI = HyperSpectralImage(createTempFolder=False)
		x = 0
		y = 0
		spectrum = [1, 2, 3, 4]
		HSI.addSpectrum(x, y, spectrum, autoSave=False)
		self.assertEqual(len(HSI.spectralPoints), 1)
		HSI.deleteSpectra()
		self.assertEqual(len(HSI.spectralPoints), 0)

	def testReturnSpectrum(self): # spectrum(self, x, y, subtractBackground=False):
		HSI = HyperSpectralImage(createTempFolder=False)
		x = 0
		y = 0
		spectrum = [1, 2, 3, 4]
		HSI.addSpectrum(x, y, spectrum, autoSave=False)
		returnSpectrum = HSI.spectrum(x, y)
		spectrum = np.array(spectrum)
		equality = np.equal(returnSpectrum, spectrum)
		result = equality.all()
		self.assertTrue(result)

	def testReturnSpectrumSubtractBackground(self):
		HSI = HyperSpectralImage(createTempFolder=False)
		x = 0
		y = 0
		spectrum = [1, 2, 3, 4]
		background = [1, 1, 1, 1]
		HSI.addSpectrum(x, y, spectrum, autoSave=False)
		HSI.setBackground(background)
		returnSpectrum = HSI.spectrum(x, y, True)
		spectrumFinal = np.array([0,1,2,3])
		equality = np.equal(returnSpectrum, spectrumFinal)
		result = equality.all()
		self.assertTrue(result)

	def testReturnSpectrumNone(self): # spectrum(self, x, y, subtractBackground=False):
		HSI = HyperSpectralImage(createTempFolder=False)
		returnSpectrum = HSI.spectrum(2, 100)
		self.assertIsNone(returnSpectrum)

	def testReturnSpectrumTypeErrorX(self): # spectrum(self, x, y, subtractBackground=False):
		HSI = HyperSpectralImage(createTempFolder=False)
		X = 0
		Y = 0
		spectrum = [1, 2, 3, 4]
		HSI.addSpectrum(X, Y, spectrum, autoSave=False)
		x = 0.1
		y = 0
		try:
			spectrum = HSI.spectrum(x, y)
		except Exception as e:
			e = str(e)
			self.assertMultiLineEqual(e, "x argument is not int.")

	def testReturnSpectrumTypeErrorY(self): # spectrum(self, x, y, subtractBackground=False):
		HSI = HyperSpectralImage(createTempFolder=False)
		X = 0
		Y = 0
		spectrum = [1, 2, 3, 4]
		HSI.addSpectrum(X, Y, spectrum, autoSave=False)
		x = 0
		y = 0.1
		try:
			spectrum = HSI.spectrum(x, y)
		except Exception as e:
			e = str(e)
			self.assertMultiLineEqual(e, "y argument is not int.")

	def testReturnSpectrumTypeErrorSubtractBackground(self): # spectrum(self, x, y, subtractBackground=False):
		HSI = HyperSpectralImage(createTempFolder=False)
		X = 0
		Y = 0
		spectrum = [1, 2, 3, 4]
		HSI.addSpectrum(X, Y, spectrum, autoSave=False)
		x = 0
		y = 0
		subtractBackground = "True"
		try:
			spectrum = HSI.spectrum(x, y, subtractBackground)
		except Exception as e:
			e = str(e)
			self.assertMultiLineEqual(e, "subtractBackground argument is not a boolean.")

	def testSetBackground(self): # setBackground(self, background):
		HSI = HyperSpectralImage(createTempFolder=False)
		background = [1, 1, 1, 1]
		HSI.setBackground(background)
		backgroundFinal = np.array([1,1,1,1])
		equality = np.equal(HSI.background, backgroundFinal)
		result = equality.all()
		self.assertTrue(result)

	def testSetBackgroundTypeError(self): # setBackground(self, background):
		HSI = HyperSpectralImage(createTempFolder=False)
		background = (1, 1, 1, 1)
		try:
			HSI.setBackground(background)
		except Exception as e:
			e = str(e)
			self.assertMultiLineEqual(e, "background argument is not a list or numpy.ndarray.")

	def testDeleteBackground(self): # deleteBackground(self):
		HSI = HyperSpectralImage(createTempFolder=False)
		background = [1, 1, 1, 1]
		HSI.setBackground(background)
		HSI.deleteBackground()
		self.assertListEqual(HSI.background, [])

	def testSetWavelength(self): # setWavelength(self, wavelength):
		HSI = HyperSpectralImage(createTempFolder=False)
		wavelength = [785, 786, 788, 789]
		HSI.setWavelength(wavelength)
		equality = np.equal(HSI.wavelength, np.array([785, 786, 788, 789]))
		result = equality.all()
		self.assertTrue(result)

	def testSetWavelengthTypeError(self): # setWavelength(self, wavelength):
		HSI = HyperSpectralImage(createTempFolder=False)
		wavelength = [785, 786, 788, 789]
		try:
			HSI.setWavelength(wavelength)
		except Exception as e:
			e = str(e)
			self.assertMultiLineEqual(e, "wavelength argument is not a list or numpy.ndarray.")

	def testDeleteWavelength(self): # deleteWavelength(self):
		HSI = HyperSpectralImage(createTempFolder=False)
		self.assertEqual(len(HSI.wavelength), 0)
		wavelength =  [785, 786, 788, 789]
		HSI.setWavelength(wavelength)
		self.assertEqual(len(HSI.wavelength), 4)
		HSI.deleteWavelength()
		self.assertEqual(len(HSI.wavelength), 0)

	def testReturnWaveNumber(self): # def waveNumber(self):
		HSI = HyperSpectralImage(createTempFolder=False)
		wavelength = [785, 786, 788, 789]
		laserWaveLength = 785
		HSI.setWavelength(wavelength)
		HSI.setLaserWavelength(laserWaveLength)
		waveNumber = HSI.waveNumber()
		equality = np.equal(waveNumber, np.array([0., 16., 48., 65.]))
		result = equality.all()
		self.assertTrue(result)

	def testReturnWaveNumberErrorLaser(self): # def waveNumber(self):
		HSI = HyperSpectralImage(createTempFolder=False)
		wavelength = [785, 786, 788, 789]
		HSI.setWavelength(wavelength)
		try:
			waveNumber = HSI.waveNumber()
		except Exception as e:
			e = str(e)
			self.assertMultiLineEqual(e, "self.excitationWavelength is not defined.")

	def testReturnWaveNumberErrorWavelength(self): # def waveNumber(self):
		HSI = HyperSpectralImage(createTempFolder=False)
		laserWaveLength = 785
		HSI.setLaserWavelength(laserWaveLength)
		try:
			waveNumber = HSI.waveNumber()
		except Exception as e:
			e = str(e)
			self.assertMultiLineEqual(e, "self.wavelength is not defined.")

	def testSetLaserWavelength(self): # setLaserWavelength(self, laser):
		HSI = HyperSpectralImage(createTempFolder=False)
		laserWaveLength = 785
		HSI.setLaserWavelength(laserWaveLength)
		self.assertEqual(HSI.excitationWavelength, 785)

	def testSetLaserWavelengthTypeError(self): # setLaserWavelength(self, laser):
		HSI = HyperSpectralImage(createTempFolder=False)
		laserWaveLength = 785.0
		try:
			HSI.setLaserWavelength(laserWaveLength)
		except Exception as e:
			e = str(e)
			self.assertMultiLineEqual(e, "excitationWavelength argument is not int.")

	def testDeleteLaserWaveLength(self): # deleteLaserWaveLength(self):
		HSI = HyperSpectralImage(createTempFolder=False)
		laserWaveLength = 785
		HSI.setLaserWavelength(laserWaveLength)
		HSI.deleteLaserWavelength()
		self.assertIsNone(HSI.excitationWavelength)

	def testMatrixRGB(self): # matrixRGB(self, colorValues, globalMaximum=True, width=None, height=None, subtractBackground=False):
		HSI = HyperSpectralImage(createTempFolder=False)
		HSI.addSpectrum(0, 0, [1, 2, 3, 4, 5, 6], autoSave=False)
		HSI.addSpectrum(0, 1, [7, 8, 9, 10, 11, 12], autoSave=False)
		HSI.addSpectrum(1, 0, [13, 14, 15, 16, 17, 18], autoSave=False)
		HSI.addSpectrum(1, 1, [19, 20, 21, 22, 23, 24], autoSave=False)
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

	def testMatrixRGBGlobalMaximumFalse(self): # matrixRGB(self, colorValues, globalMaximum=True, width=None, height=None, subtractBackground=False):
		HSI = HyperSpectralImage(createTempFolder=False)
		HSI.addSpectrum(0, 0, [1, 2, 3, 4, 5, 6], autoSave=False)
		HSI.addSpectrum(0, 1, [7, 8, 9, 10, 11, 12], autoSave=False)
		HSI.addSpectrum(1, 0, [13, 14, 15, 16, 17, 18], autoSave=False)
		HSI.addSpectrum(1, 1, [19, 20, 21, 22, 23, 24], autoSave=False)

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

	def testMatrixRGBWithWidthAndHeightInInput(self): # matrixRGB(self, colorValues, globalMaximum=True, width=None, height=None, subtractBackground=False):
		HSI = HyperSpectralImage(createTempFolder=False)
		HSI.addSpectrum(0, 0, [1, 2, 3, 4, 5, 6], autoSave=False)
		HSI.addSpectrum(0, 1, [7, 8, 9, 10, 11, 12], autoSave=False)
		colorValues = ColorValues(0, 1/3, 1/3, 2/3, 2/3, 1)
		matrix = HSI.matrixRGB(colorValues, width=2, height=2)

		testMatrix = np.zeros((2, 2, 3))
		testMatrix[0][0] = np.array([3, 7, 11])
		testMatrix[1][0] = np.array([15, 19, 23])
		testMatrix[0][1] = np.array([0, 0, 0])
		testMatrix[1][1] = np.array([0, 0, 0])
		testMatrix = (testMatrix / np.max(testMatrix)) * 255
		testMatrix = testMatrix.round(0)

		equality = np.equal(matrix, testMatrix)
		result = equality.all()
		self.assertTrue(result)

	def testMatrixRGBSubtractBackgroundTrue(self): # matrixRGB(self, colorValues, globalMaximum=True, width=None, height=None, subtractBackground=False):
		HSI = HyperSpectralImage(createTempFolder=False)
		HSI.addSpectrum(0, 0, [1, 2, 3, 4, 5, 6], autoSave=False)
		HSI.addSpectrum(0, 1, [7, 8, 9, 10, 11, 12], autoSave=False)
		HSI.addSpectrum(1, 0, [13, 14, 15, 16, 17, 18], autoSave=False)
		HSI.addSpectrum(1, 1, [19, 20, 21, 22, 23, 24], autoSave=False)
		HSI.setBackground([1,1,1,1,1,1])
		colorValues = ColorValues(0, 1/3, 1/3, 2/3, 2/3, 1)
		matrix = HSI.matrixRGB(colorValues, subtractBackground=True)

		testMatrix = np.zeros((2, 2, 3))
		testMatrix[0][0] = np.array([1, 5, 9])
		testMatrix[1][0] = np.array([13, 17, 21])
		testMatrix[0][1] = np.array([25, 29, 33])
		testMatrix[1][1] = np.array([37, 41, 45])
		testMatrix = (testMatrix / np.max(testMatrix)) * 255
		testMatrix = testMatrix.round(0)

		equality = np.equal(matrix, testMatrix)
		result = equality.all()
		self.assertTrue(result)

	def testMatrixRGBWithNoData(self): # matrixRGB(self, colorValues, globalMaximum=True, width=None, height=None, subtractBackground=False):
		HSI = HyperSpectralImage(createTempFolder=False)
		colorValues = ColorValues(0, 1/3, 1/3, 2/3, 2/3, 1)
		matrix = HSI.matrixRGB(colorValues)
		self.assertIsNone(matrix)

	def testSaveImage(self): # saveImage(self, matrixRGB):
		HSI = HyperSpectralImage(createTempFolder=False)
		HSI.addSpectrum(0, 0, [1, 1, 1], autoSave=False)
		HSI.addSpectrum(0, 1, [1, 0, 0], autoSave=False)
		HSI.addSpectrum(1, 0, [0, 1, 0], autoSave=False)
		HSI.addSpectrum(1, 1, [0, 0, 1], autoSave=False)
		colorValues = ColorValues(0, 1/3, 1/3, 2/3, 2/3, 1)
		matrix = HSI.matrixRGB(colorValues)
		


	# /////////////////////////////////////////////////////////////////////////////////
	# Non-publics functions

	def testReturnWidthImage(self):
		HSI = HyperSpectralImage(createTempFolder=False)
		HSI.addSpectrum(0, 0, [1, 2, 3], autoSave=False)
		HSI.addSpectrum(0, 1, [4, 5, 6], autoSave=False)
		HSI.addSpectrum(1, 0, [7, 8, 9], autoSave=False)
		HSI.addSpectrum(1, 1, [10, 11, 12], autoSave=False)
		HSI.addSpectrum(2, 0, [13, 14, 15], autoSave=False)
		HSI.addSpectrum(2, 1, [16, 17, 18], autoSave=False)

		width = HSI.width()
		self.assertEqual(width, 3)

	def testReturnWidthImageWithNoData(self):
		HSI = HyperSpectralImage(createTempFolder=False)
		width = HSI.width()
		self.assertEqual(width, 0)

	def testReturnHeightImage(self):
		HSI = HyperSpectralImage(createTempFolder=False)
		HSI.addSpectrum(0, 0, [1, 2, 3], autoSave=False)
		HSI.addSpectrum(0, 1, [4, 5, 6], autoSave=False)
		HSI.addSpectrum(1, 0, [7, 8, 9], autoSave=False)
		HSI.addSpectrum(1, 1, [10, 11, 12], autoSave=False)
		HSI.addSpectrum(2, 0, [13, 14, 15], autoSave=False)
		HSI.addSpectrum(2, 1, [16, 17, 18], autoSave=False)

		width = HSI.height()
		self.assertEqual(width, 2)

	def testReturnHeightImageWithNoData(self):
		HSI = HyperSpectralImage(createTempFolder=False)
		width = HSI.height()
		self.assertEqual(width, 0)

	def testReturnSpectrumLen(self):
		HSI = HyperSpectralImage(createTempFolder=False)
		x = 0
		y = 0
		spectrum = [1, 2, 3, 4]
		HSI.addSpectrum(x, y, spectrum, autoSave=False)
		spectrumLen = HSI.spectrumLen()

	def testReturnSpectrumLenWithNoData(self):
		HSI = HyperSpectralImage(createTempFolder=False)
		spectrumLen = HSI.spectrumLen()
		self.assertIsNone(spectrumLen)

	def testReturnSpectrumRange(self):
		HSI = HyperSpectralImage(createTempFolder=False)
		wavelength = [785, 786, 788, 789]
		HSI.setWavelength(wavelength)
		spectrumRange = HSI.spectrumRange()
		self.assertEqual(spectrumRange, 4)


	def testReturnSpectrumRangeNone(self):
		HSI = HyperSpectralImage(createTempFolder=False)
		spectrumRange = HSI.spectrumRange()
		self.assertIsNone(spectrumRange)

	def testMatrixData(self):
		HSI = HyperSpectralImage(createTempFolder=False)
		HSI.addSpectrum(0, 0, [1, 2, 3], autoSave=False)
		HSI.addSpectrum(0, 1, [4, 5, 6], autoSave=False)
		HSI.addSpectrum(1, 0, [7, 8, 9], autoSave=False)
		HSI.addSpectrum(1, 1, [10, 11, 12], autoSave=False)
		HSI.addSpectrum(2, 0, [13, 14, 15], autoSave=False)
		HSI.addSpectrum(2, 1, [16, 17, 18], autoSave=False)

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
		HSI = HyperSpectralImage(createTempFolder=False)
		matrix = HSI.matrixData()
		self.assertIsNone(matrix)

	def testFindMaximum(self):
		HSI = HyperSpectralImage(createTempFolder=False)
		HSI.addSpectrum(0, 0, [1, 2, 3, 4, 5, 6], autoSave=False)
		HSI.addSpectrum(0, 1, [7, 8, 9, 10, 11, 12], autoSave=False)
		HSI.addSpectrum(1, 0, [13, 14, 15, 16, 17, 18], autoSave=False)
		HSI.addSpectrum(1, 1, [19, 20, 21, 22, 23, 24], autoSave=False)


if __name__ == "__main__":
    unittest.main()