#!/usr/bin/python

import os

from common import get_batch_number

print(batch := get_batch_number())
os.system(f"scp -r kdm:/srv/scratch/z5358697/aa-prep/{batch} aa-prep/")
