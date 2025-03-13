#!/usr/bin/bash

mypy 01-run-gauss.py || exit 1
pylint 01-run-gauss.py || exit 1
python 01-run-gauss.py
