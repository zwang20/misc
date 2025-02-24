#!/usr/bin/python
import numpy as np
from scipy.optimize import curve_fit
velocities = []
with open("raw.dat") as f:
    for line in f:
        velocities.append(float(line))
print(velocities)

def maxwell_boltzmann(x_data: list, a0: float):
    HYDROGEN_MASS = 1.0080000162124634
    a0 = float(a0)
    output = []
    for x in x_data:
        assert x > 0
        output.append(np.sqrt((2 * HYDROGEN_MASS ** 3)/(np.pi * a0 ** 3)) * x ** 2 * np.exp(- (HYDROGEN_MASS * x ** 2) / (2 * a0)))
    return output

histogram = np.histogram(velocities, bins=100, density=True)
heights, x_edges = histogram
x_centers = (x_edges[:-1] + x_edges[1:]) / 2
temperature = curve_fit(maxwell_boltzmann, x_centers, heights, 0.6)
print(f"a0: {temperature[0][0]}, b: {temperature[1][0]}")
temperature = temperature[0][0]/0.00198657
print(f"temperature: {temperature}")
