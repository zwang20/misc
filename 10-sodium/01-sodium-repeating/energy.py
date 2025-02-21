#!/usr/bin/python

# 1. generate the energies using get_energy.tcl
#    specically, "vmd -dispdev text -e get_energy.tcl"

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit


def maxwell_boltzmann(x_data: list, a0: float):
	a0 = float(a0)
	output = []
	for x in x_data:
		assert x > 0
		output.append((2/np.sqrt(np.pi*np.pow(a0, 3))) * np.sqrt(x) * np.exp(-x / a0))
	return output

with open("energy.dat", "r") as input_file:
	energies = [float(i) for i in input_file.readlines()]
histogram = np.histogram(energies, bins=100, density=True)
heights, x_edges = histogram
x_centers = (x_edges[:-1] + x_edges[1:]) / 2
plt.hist(energies, bins=100,density=True)
temperature = curve_fit(maxwell_boltzmann, x_centers, heights, 0.6)
print(temperature)
plt.plot(x_centers, maxwell_boltzmann(x_centers, temperature[0][0]))
plt.plot(x_centers, maxwell_boltzmann(x_centers, 0.6), 'r')
plt.show()
	# with open("energy.csv", "w") as output_file:
	# 	l = sorted(input_file.readlines())
	# 	for i, j in enumerate(l):
	# 		output_file.write(f"{i},{j}")
