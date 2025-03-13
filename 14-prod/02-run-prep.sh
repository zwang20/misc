#!/usr/bin/bash

mypy 02-run-prep.py || exit 1
pylint 02-run-prep.py || exit 1
python 02-run-prep.py
