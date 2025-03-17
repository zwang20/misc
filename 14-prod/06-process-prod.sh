#!/usr/bin/bash

mypy 06-process-prod.py || exit 1
pylint 06-process-prod.py || exit 1
python 06-process-prod.py
