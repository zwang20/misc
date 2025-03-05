#!/usr/bin/bash

set -e
black -l 200 plot_fep.py
mypy plot_fep.py
python plot_fep.py
