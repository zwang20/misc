#!/usr/bin/python

folder_prefix = "one"

# ask user for input

time_ns = int(input("Input time (ns): "))

# calculate relavent stuff
import math

# maxiumu = 2.0
step_time = 1.0

print(f"{step_time=}fs")

steps = time_ns * 1000 // step_time

print(f"{steps=}")

dcd = math.ceil(steps / 200)

print(f"{dcd=}")

print()

import os
print("creating directory")
os.system(f"mkdir -p '{folder_prefix}_{time_ns}'")

print("copying files")
os.system(f"cp ionized.pdb 'sodium_{time_ns}/'")
os.system(f"cp ionized.psf 'sodium_{time_ns}/'")
os.system(f"cp par_all27_prot_lipid.inp 'sodium_{time_ns}/'")
os.system(f"cp run.sh 'sodium_{time_ns}/one_{time_ns}'")

sodium_namd_template = f"""
#############################################################
## JOB DESCRIPTION                                         ##
#############################################################

# Minimization and Equilibration of
# Ubiquitin in a Water Sphere


#############################################################
## ADJUSTABLE PARAMETERS                                   ##
#############################################################

structure          ionized.psf
coordinates        ionized.pdb

set temperature    298
set outputname     output

firsttimestep      0


#############################################################
## SIMULATION PARAMETERS                                   ##
#############################################################

# Input
paraTypeCharmm      on
parameters          par_all27_prot_lipid.inp
temperature         $temperature


# Force-Field Parameters
exclude             scaled1-4
1-4scaling          1.0
cutoff              12.0
switching           on
switchdist          10.0
pairlistdist        14.0


# Integrator Parameters
timestep            {step_time}
rigidBonds          all  ;# needed for 2fs steps
nonbondedFreq       1
fullElectFrequency  2
stepspercycle       10


# Constant Temperature Control
langevin            on   ;# do langevin dynamics
langevinDamping     1    ;# damping coefficient (gamma) of 1/ps
langevinTemp        $temperature
langevinHydrogen    off  ;# don't couple langevin bath to hydrogens

# Electrostatic Force Evaluation
MSM                 on
MSMGridSpacing      2.5  ;# very sensitive to performance, use this default
MSMxmin            -5.0
MSMxmax             60.0
MSMymin            -5.0
MSMymax             60.0
MSMzmin            -15.0
MSMzmax             46

# Output
outputName          $outputname

#restartfreq         500  ;# 500steps = every 1ps
outputEnergies {dcd}
dcdfreq {dcd}
outputTiming {dcd}


#############################################################
## EXTRA PARAMETERS                                        ##
#############################################################

# Repeating unit cells

# Periodic Boundary Conditions
cellBasisVector1    30.0    0.   0.0
cellBasisVector2     0.0  30.0   0.0
cellBasisVector3     0.0    0   30.0
cellOrigin          0.0   0.0  0.0

wrapAll             on


#############################################################
## EXECUTION SCRIPT                                        ##
#############################################################

# Minimization
minimize            100
reinitvels          $temperature

run {steps};
"""

print("writing sodium.namd")
with open(f"one_{time_ns}/sodium.namd", 'w') as f:
    f.write(sodium_namd_template)
