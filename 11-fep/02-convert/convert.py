#!/usr/bin/python

# **attempts** to convert input files into files usable by namd
# because freesolv seems to support everything but

import parmed as pmd
print("remember to source venv")

gmx_top = pmd.load_file('mobley_9055303.top', xyz='mobley_9055303.gro')
gmx_top.save('output.psf')
gmx_top.save('output.pdb')
