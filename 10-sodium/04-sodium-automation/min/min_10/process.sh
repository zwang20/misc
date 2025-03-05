#!/usr/bin/bash

rm energy.dat
vmd -dispdev text -e get_energy.tcl < /dev/null
./energy.py
