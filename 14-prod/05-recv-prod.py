#!/usr/bin/python

import os

from common import get_batch_number

print(batch := get_batch_number())
os.system(f"rsync -rP kdm:/srv/scratch/z5358697/ab-prod/ ab-prod/")
