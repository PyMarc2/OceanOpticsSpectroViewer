import matplotlib
import seabreeze.spectrometers as sb
import numpy as np
import time
import os

matplotlib.use('TKAgg')

from matplotlib import pyplot as plt

devices = sb.list_devices()
print(devices)


timeInSec = 10
integrationTimeInMicros = 500000  # 1500
graphRefresh = 1
name = "HG_water_{}s".format(timeInSec)  # mardi : 1j, lundi : 7j

spec = sb.Spectrometer(devices[0])
spec.integration_time_micros(integrationTimeInMicros)

waves = spec.wavelengths()[2:]
intens = spec.intensities()[2:]

maxi = 0
mini = 10000

fig, ax = plt.subplots()
graph, = ax.plot(waves, intens)
plt.xlabel("Longueur d'onde [nm]")
plt.ylabel("Intensité")
plt.pause(0.05)

deltaT = 0
t = time.time()

data = []
while deltaT < timeInSec:
    intens = []
    for j in range(graphRefresh):
        intens.append(spec.intensities()[2:])
    intens = np.mean(intens, axis=0)

    data.append(intens)
    graph.set_ydata(np.mean(data, axis=0))  # (intens)
    if min(intens) < mini:
        mini = min(intens)
    if max(intens) > maxi:
        maxi = max(intens)

    plt.ylim(mini, maxi)
    plt.pause(0.01)
    deltaT = time.time() - t

data = np.mean(data, axis=0)

waves = waves[np.newaxis].T
data = data[np.newaxis].T

arr = np.hstack((waves, data))

num = 0
while os.path.exists("data_hg/{}_{}.txt".format(name, num)):
    num += 1
np.savetxt("data_hg/{}_{}.txt".format(name, num), arr, newline="\n")
