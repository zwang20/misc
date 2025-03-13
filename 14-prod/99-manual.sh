#!/usr/bin/bash

mypy 99-manual.py || exit 1
pylint 99-manual.py || exit 1
python 99-manual.py
