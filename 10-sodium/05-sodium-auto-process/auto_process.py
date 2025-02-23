#!/usr/bin/python

prefix = "hless"

import os
import numpy as np
# import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import natsort
import subprocess

def maxwell_boltzmann(x_data: list, a0: float):
	a0 = float(a0)
	output = []
	for x in x_data:
		assert x > 0
		output.append((2/np.sqrt(np.pi*np.pow(a0, 3))) * np.sqrt(x) * np.exp(-x / a0))
	return output



print(f"{prefix=}")

os.chdir(prefix)

print(f"{os.getcwd()=}")

folders = natsort.natsorted(filter(lambda x: os.path.isdir(x), os.listdir()))

print(f"{folders=}")

os.chdir('..')

print(f"{os.getcwd()=}")

outputs = []
md5sums = []

for folder in folders:
    print(f"{folder=}")
    os.system(f"cp '{prefix}/{folder}/output.vel' .")
    md5sum = (
        subprocess.run(["md5sum", "output.vel"], capture_output=True)
        .stdout
        .decode('utf-8')
        .split()[0]
    )
    assert md5sum not in md5sums
    md5sums.append(md5sum)
    output_file = natsort.natsorted(filter(lambda x: os.path.isfile(f"{prefix}/{folder}/{x}") and x.startswith(folder), os.listdir(f"{prefix}/{folder}")))[-1]
    print(f"{output_file=}")
    with open(f"{prefix}/{folder}/{output_file}") as f:
        assert "Job execution was successful. Exit Status 0." in f.read()
    processor = (subprocess.run(["grep", "^Model name", f"{prefix}/{folder}/{output_file}"], capture_output=True).stdout.decode('utf-8').split('\n')[0].split(':')[1].strip())

    # TODO: fixme
    hostname = (subprocess.run(["grep", "^k...", f"{prefix}/{folder}/{output_file}"], capture_output=True).stdout.decode('utf-8').split('\n')[0].strip())

    walltime = (subprocess.run(["grep", "^Walltime: ", f"{prefix}/{folder}/{output_file}"], capture_output=True).stdout.decode('utf-8').split('\n')[0].split(':', 1)[1].split()[0])
    os.system("vmd -dispdev text -e get_energy.tcl < /dev/null")
    subprocess.run(["vmd", "-dispdev", "text", "-e", "get_energy.tcl"], stdin=subprocess.DEVNULL).check_returncode()
    with open("energy.dat", "r") as input_file:
        energies = [float(i) for i in input_file.readlines()]
    histogram = np.histogram(energies, bins=100, density=True)
    heights, x_edges = histogram
    x_centers = (x_edges[:-1] + x_edges[1:]) / 2
    temperature = curve_fit(maxwell_boltzmann, x_centers, heights, 0.6)
    print(f"a0: {temperature[0][0]}, b: {temperature[1][0]}")
    temperature = temperature[0][0]/0.00198657
    print(f"temperature: {temperature}")
    # outputs.append((folder, temperature))
    outputs.append((walltime, 16, hostname, processor, folder, temperature))
    for a, b, c, d, e, f in outputs:
        print(f"{a},{b},{c},{d},{e},{f}")

