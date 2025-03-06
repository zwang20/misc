#!/usr/bin/python
import matplotlib.pyplot as plt

molecules: dict[str, tuple[float, float, str, int]] = dict()


def update_molecule(molecule: str, energy: float, name: str):
    if molecule in molecules:
        if energy < molecules[molecule][0]:
            molecules[molecule] = (
                energy,
                molecules[molecule][1],
                molecules[molecule][2],
                molecules[molecule][3] + 1,
            )
        elif energy > molecules[molecule][1]:
            molecules[molecule] = (
                molecules[molecule][0],
                energy,
                molecules[molecule][2],
                molecules[molecule][3] + 1,
            )
        else:
            molecules[molecule] = (
                molecules[molecule][0],
                molecules[molecule][1],
                molecules[molecule][2],
                molecules[molecule][3] + 1,
            )
    else:
        molecules[molecule] = (energy, energy, name, 1)


def read_line(line: str):
    if line.startswith("mobley_"):
        line = line.split(";")
        update_molecule(line[0].strip(), float(line[5]), line[2].strip())


with open("v0.1.txt") as f:
    for l in f:
        read_line(l)
with open("v0.2.txt") as f:
    for l in f:
        read_line(l)
with open("v0.3.txt") as f:
    for l in f:
        read_line(l)
with open("v0.5.txt") as f:
    for l in f:
        read_line(l)

print("generating graph")
x = list()
for v in molecules.values():
    if v[3] > 3:
        x.append(v[1] - v[0])
plt.hist(x, bins=100)
plt.show()
