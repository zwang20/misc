#!/usr/bin/bash

mypy 00-pick.py || exit 1
pylint 00-pick.py || exit 1
python 00-pick.py
