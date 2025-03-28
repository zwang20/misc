#!/usr/bin/python

import sys

import pymbar
import numpy as np

assert len(sys.argv) == 3, (
    "Usage: mbar.py <forward> <backward>",
    sys.argv,
    len(sys.argv),
)

temperature = 300


for i in pymbar.testsystems.HarmonicOscillatorsTestCase().sample(mode="u_kn"):
    print(i)
    print(i.shape)
    print("=" * 20)
