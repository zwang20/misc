#!/usr/bin/python

import os
import subprocess

# check for fake frequencies
os.system("grep ' Frequencies --' */*.log")
