#!/usr/bin/python

"""
Script to parse and plot free energy changes
"""

import matplotlib.pyplot as plt

forward_x: list[float] = []
forward_y: list[float] = []
backward_x: list[float] = []
backward_y: list[float] = []

with open("ParseFEP.log") as f:
    for line in f:
        words = line.split()
        if len(words) == 5:
            if words[0] == "forward:":
                forward_x.append(float(words[1]))
                forward_y.append(float(words[3]))
            elif words[0] == "backward:":
                backward_x.append(float(words[1]))
                backward_y.append(float(words[3]))
plt.plot(forward_x, forward_y, label="forward")
plt.plot(backward_x, backward_y, label="backward")
plt.legend()
plt.show()
