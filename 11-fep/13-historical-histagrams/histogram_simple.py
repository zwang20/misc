#!/usr/bin/python

from scipy.stats import norm
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt


# v1 = dict()
# with open("v0.1.txt") as f:
#     for line in f:
#         if line.startswith("mobley_"):
#             line = line.split(";")
#             v1[line[0].strip()] = float(line[5])
#
# v2 = dict()
# with open("v0.3.txt") as f:
#     for line in f:
#         if line.startswith("mobley_"):
#             line = line.split(";")
#             v2[line[0].strip()] = float(line[5])
#
#
# diff = list()
# for k in v1:
#     if k in v2:
#         diff.append(v2[k] - v1[k])

# plt.title("Differences between FreeSolv v0.1 and Freesolv v0.5")

plt.xlabel("Difference (kcal/mol)")
plt.ylabel("Distribution")

extra_data = """
-0.2379118158
0.01926301397
-0.02040789575
0.05720909588
0.008913191342
0.05676078206
-0.03542140986
0.04626283421
-0.0496142232
0.07683112459
0.03626698281
0.02191151369
-0.523952676
0.5993076624
-0.1853533536
""".strip().split()
diff = list(float(i) for i in extra_data)
n, bins, patches = plt.hist(diff, bins=25, density=True)
bins = (bins[1:] + bins[:-1]) / 2
# for i, j in zip(bins, n):
#     print(f"{i},{j}")
from scipy.optimize import curve_fit
import numpy as np


def gauss(x, mu, sigma):
    y = 1 / (sigma * np.sqrt(2 * np.pi)) * np.exp(-1 / 2 * np.square((x - mu) / sigma))
    return y


parameters, covariance = curve_fit(gauss, bins, n)
print(parameters)
print(parameters.shape)
print(covariance)
mu, sigma = parameters

xnew = np.linspace(min(bins), max(bins), 500)
ynew = gauss(xnew, mu, sigma)
l = plt.plot(xnew, ynew, "r", linewidth=1)
plt.title(
    r"$\mathrm{Differences\ between\ Standard\ and\ Frozen\ Methods:}\ \mu=%.3f,\ \sigma=%.3f$"
    % (mu, sigma)
)
plt.show()
plt.show()
