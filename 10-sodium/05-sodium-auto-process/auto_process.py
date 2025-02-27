#!/usr/bin/python

prefix = "hmore"

import os
import logging
from collections.abc import Iterator, Callable

import numpy as np
from numpy.typing import ArrayLike
from scipy.optimize import curve_fit  # type: ignore[import-untyped]
import natsort
import subprocess

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def maxwell_boltzmann_energy_fn(x_data: list[float], a0: float) -> list[float]:
    a0 = float(a0)
    output = []
    for x in x_data:
        assert x > 0
        output.append(
            (2 / np.sqrt(np.pi * np.pow(a0, 3))) * np.sqrt(x) * np.exp(-x / a0)
        )
    return output


def maxwell_boltzmann_velocity_generator(
    mass: float,
) -> Callable[[list[float], float], list[float]]:
    def maxwell_boltzmann_velocity_fn(x_data: list[float], a0: float) -> list[float]:
        a0 = float(a0)
        output = []
        for x in x_data:
            assert x > 0
            output.append(
                np.sqrt((2 * mass**3) / (np.pi * a0**3))
                * x**2
                * np.exp(-(mass * x**2) / (2 * a0))
            )
        return output

    return maxwell_boltzmann_velocity_fn


def histogram_fit(
    data: list[float], fn: Callable[[list[float], float], list[float]]
) -> tuple[float, float, float]:
    histogram = np.histogram(data, bins=1000, density=True)
    heights, x_edges = histogram
    x_centers = (x_edges[:-1] + x_edges[1:]) / 2
    temperature = curve_fit(fn, x_centers, heights, 0.6)
    # print(f"a0: {temperature[0][0]}, b: {temperature[1][0]}")
    # temperature = temperature[0][0] / 0.00198657
    return temperature[0][0], temperature[1][0][0], temperature[0][0] / 0.00198657


print(f"{prefix=}")

os.chdir(prefix)

print(f"{os.getcwd()=}")

folders = natsort.natsorted(filter(lambda x: os.path.isdir(x), os.listdir()))

print(f"{folders=}")

os.chdir("..")

print(f"{os.getcwd()=}")

outputs = []
md5sums = []

for folder in folders:
    print(f"{folder=}")
    subprocess.run(["cp", f"{prefix}/{folder}/output.vel", "."]).check_returncode()
    md5sum = (
        subprocess.run(["md5sum", "output.vel"], capture_output=True)
        .stdout.decode("utf-8")
        .split()[0]
    )
    assert md5sum not in md5sums
    md5sums.append(md5sum)
    output_file = natsort.natsorted(
        filter(
            lambda x: os.path.isfile(f"{prefix}/{folder}/{x}") and x.startswith(folder),
            os.listdir(f"{prefix}/{folder}"),
        )
    )[-1]
    print(f"{output_file=}")
    with open(f"{prefix}/{folder}/{output_file}") as f:
        assert "Job execution was successful. Exit Status 0." in f.read()
    processor = (
        subprocess.run(
            ["grep", "^Model name", f"{prefix}/{folder}/{output_file}"],
            capture_output=True,
        )
        .stdout.decode("utf-8")
        .split("\n")[0]
        .split(":")[1]
        .strip()
    )

    # TODO: fixme
    hostname = (
        subprocess.run(
            ["grep", "^k...", f"{prefix}/{folder}/{output_file}"], capture_output=True
        )
        .stdout.decode("utf-8")
        .split("\n")[0]
        .strip()
    )

    walltime = (
        subprocess.run(
            ["grep", "^Walltime: ", f"{prefix}/{folder}/{output_file}"],
            capture_output=True,
        )
        .stdout.decode("utf-8")
        .split("\n")[0]
        .split(":", 1)[1]
        .split()[0]
    )

    print("Running vmd process")
    vmd_process: subprocess.CompletedProcess = subprocess.run(
        ["vmd", "-dispdev", "text", "-e", "get_energy.tcl"],
        capture_output=True,
        stdin=subprocess.DEVNULL,
    )
    if vmd_process.returncode != 0:
        logger.error(f"vmd process exited with code {vmd_process.returncode}")
        logger.error("stdout")
        logger.error(vmd_process.stdout.decode("utf-8"))
        logger.error("stderr")
        logger.error(vmd_process.stderr.decode("utf-8"))
        assert False

    mass_velocity_squared_list: list[tuple[float, float]] = []
    with open("mass_velocities.dat", "r") as f:
        for line in f:
            mass, velocity = line.split(",", 1)
            mass_velocity_squared_list.append((float(mass), float(velocity)))

    # calculate temperature from energy
    energies = [
        1 / 2 * mass * velocity_squared
        for mass, velocity_squared in mass_velocity_squared_list
    ]
    a0, b, temperature = histogram_fit(energies, maxwell_boltzmann_energy_fn)
    logger.info(f"{a0=}, {b=}, {temperature=}")

    if b > 0.001:
        logger.warn(f"{folder} error > 0.001, check input")

    outputs.append((walltime, 16, hostname, processor, folder, temperature))
    # calculate temperature from hydrogen
    # hydrogen_velocity_squared = [
    #     velocity_squared
    #     for mass, velocity_squared in mass_velocity_squared_list
    #     if mass < 1.009
    # ]
    # print(
    #     "Hydrogen: ",
    #     histogram_fit(
    #         hydrogen_velocity_squared,
    #         maxwell_boltzmann_velocity_generator(1.0080000162124634),
    #     ),
    # )

    # calculate temperature from oxygen
    # oxygen_velocity_squared = [
    #     velocity_squared
    #     for mass, velocity_squared in mass_velocity_squared_list
    #     if 15.9 < mass < 16.0
    # ]
    # print(
    #     "Oxygen: ",
    #     histogram_fit(
    #         hydrogen_velocity_squared,
    #         maxwell_boltzmann_velocity_generator(15.99940013885498),
    #     ),
    # )

    for a, b, c, d, e, f in outputs:
        print(f"{a},{b},{c},{d},{e},{f}")
