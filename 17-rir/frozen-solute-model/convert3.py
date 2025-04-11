"""
convert3

converts runs if and only if the conf is the same in step 2 and 3
"""

import os
import sqlite3
import subprocess

con = sqlite3.connect("frozen_solute_model_new.db")
cur = con.cursor()
