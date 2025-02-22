#!/usr/bin/python

# maximum = 2.0
step_time = 1.0
damping = 0.5
folder_prefix = "less"

# ask user for input

time_ns = int(input("Input time (ns): "))

# calculate relavent stuff
import math


print(f"{step_time=}fs")

steps = int(time_ns * 1000 // step_time)

print(f"{steps=}")

dcd = math.ceil(steps / 200)

print(f"{dcd=}")

print()

import os
print("creating directory")
os.system(f"mkdir -p '{folder_prefix}_{time_ns}'")

print("copying files")
os.system(f"cp ionized.pdb '{folder_prefix}_{time_ns}/'")
os.system(f"cp ionized.psf '{folder_prefix}_{time_ns}/'")
os.system(f"cp par_all27_prot_lipid.inp '{folder_prefix}_{time_ns}/'")

run_template=f"""#!/bin/bash
#PBS -l walltime=12:00:00
#PBS -l mem=200Mb
#PBS -l ncpus=16
#PBS -j oe

# add modules
#module purge
#module add namd/2.14

# run job
cd ${{PBS_O_WORKDIR}} || exit 1

# delete previous
rm output.*

# print info
hostname
nproc
lscpu | grep "Model name"

# run program
PATH="/srv/scratch/z5358697/namd:$PATH" namd3 +p$(nproc) sodium.namd || qsub '{folder_prefix}_{time_ns}'

# print cpuinfo
hostname
nproc
lscpu | grep "Model name"
"""

# os.system(f"cp run.sh '{folder_prefix}_{time_ns}/{folder_prefix}_{time_ns}'")
with open(f"{folder_prefix}_{time_ns}/{folder_prefix}_{time_ns}", 'w') as f:
    f.write(run_template)

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
fullElectFrequency  1
stepspercycle       10


# Constant Temperature Control
langevin            on   ;# do langevin dynamics
langevinDamping     {damping}    ;# damping coefficient (gamma) of 1/ps
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
with open(f"{folder_prefix}_{time_ns}/sodium.namd", 'w') as f:
    f.write(sodium_namd_template)
