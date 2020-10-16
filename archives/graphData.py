import numpy as np
import matplotlib
import os
matplotlib.use('TKAgg')
import matplotlib.pyplot as plt

files = ["data/{}".format(file) for file in os.listdir("../data/") if ".txt" in file]

minCut = 0
maxCut = -1

Ref = np.loadtxt(files[0])[:, 1]
Ref2 = np.loadtxt(files[1])[:, 1]
Ref -= np.mean(Ref[300:500])
Ref2 -= np.mean(Ref2[300:500])

dataRefY = (Ref[minCut:maxCut]/np.max(Ref[minCut:maxCut]) + Ref2[minCut:maxCut]/np.max(Ref2[minCut:maxCut])) / 2

for file in files[2:]:
    data = np.loadtxt(file)
    dataY = data[minCut:maxCut, 1]
    dataY -= np.mean(dataY[300:500])
    dataY /= np.max(dataY)

    # plt.plot(data[:, 0], dataY, label=file)
    c = "black" if "vide" in file else "blue"
    c = "purple" if "waterClean" in file else c
    c = "orange" if "caustique" in file else c
    plt.plot(data[minCut:maxCut, 0], dataY - dataRefY, label="$\Delta$ {}".format(file), color=c)
    plt.plot()

plt.legend(loc='best')
plt.show()
