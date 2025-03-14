#!/usr/bin/bash

mypy 04-run-prod.py || exit 1
pylint 04-run-prod.py || exit 1
python 04-run-prod.py
