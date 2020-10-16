import numpy as np
import matplotlib
from scipy.ndimage import gaussian_filter1d
import os
matplotlib.use('TKAgg')
import matplotlib.pyplot as plt

files = ["data_19-05-27/{}".format(file) for file in os.listdir("../data/data_19-05-27/") if ".txt" in file]
# files = ["data_hg/{}".format(file) for file in os.listdir("data_hg/") if ".txt" in file]

minCut = 100
maxCut = 3000

# Ref = np.loadtxt(files[0])[:, 1]
# Ref2 = np.loadtxt(files[1])[:, 1]
# Ref -= np.mean(Ref[300:500])
# Ref2 -= np.mean(Ref2[300:500])

# dataRefY = (Ref[minCut:maxCut]/np.max(Ref[minCut:maxCut]) + Ref2[minCut:maxCut]/np.max(Ref2[minCut:maxCut])) / 2

for i, file in enumerate(files):
    data = np.loadtxt(file)
    dataY = data[minCut:maxCut, 1]
    dataY -= np.mean(dataY[300:500])
    dataY /= np.mean(dataY)

    FdataY = gaussian_filter1d(dataY, 10)

    # plt.plot(data[:, 0], dataY, label=file)
    c = "black" if "clean" in file else "blue"
    c = "purple" if "1j" in file else c
    c = "orange" if "7j" in file else c
    # lstyle = "--" if "5s" in file else "-"
    # plt.plot(data[minCut:maxCut, 0], dataY - dataRefY, label="$\Delta$ {}".format(file), color=c)
    # plt.plot(data[minCut:maxCut, 0], dataY, label="$\Delta$ {}".format(file), color=c)
    label = file.split("/")[1][:-6].replace("_100s", "").replace("_5s", "") if i in [0, 9, 15, 18] else None
    plt.plot(data[minCut:maxCut, 0], FdataY, label=label, color=c)  # , linestyle=lstyle)


plt.ylabel("Intensity")
plt.xlabel("Wavelength [nm]")
plt.legend(loc='best')
plt.show()
