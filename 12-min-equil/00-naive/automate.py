#!/usr/bin/python
import os
import subprocess

tleap_template = """
source leaprc.gaff2
source leaprc.water.tip3p
mol = loadMol2 mobley_{prefix}.mol2
check mol
solvatebox mol TIP3PBOX 15
check mol
savepdb mol mobley_{prefix}.pdb
saveamberparm mol mobley_{prefix}.prmtop mobley_{prefix}.inpcrd
quit
"""

generic_template = """
{io}

set temperature     300  ;# target temperature used several times below

restartfreq         5000     ;# 1000 steps = every 1ps
dcdfreq             5000

outputEnergies      5000       ;# 100 steps = every 0.2 ps
outputpressure      5000
XSTFreq             5000

# Force-Field Parameters
amber               on
parmfile            mobley_{prefix}.prmtop


# system dimensions
cellBasisVector1                {x}     0.000   0.000
cellBasisVector2                0.000   {y}     0.000
cellBasisVector3                0.000   0.000   {z}
cellOrigin                      0.000   0.000   0.000

wrapAll             on
wrapWater           on

# PME (for full-system periodic electrostatics)
PME                 yes
PMEGridSpacing      1.0

# These are specified by AMBER
readexclusions      yes      # from Sergey?
exclude             scaled1-4
1-4scaling          0.833333   # for Amber
scnb                2.0     # for Amber
cutoff              9.0
switching           off
switchdist          8.0     # from Sergey mdin_namd
pairlistdist        11.0    # from Sergey mdin_namd

stepspercycle       10   ;# redo pairlists every ten steps
margin              1.0

# Integrator Parameters
timestep            2.0  ;# 2fs/step
rigidBonds          all  ;# needed for 2fs steps
nonbondedFreq       1    ;# nonbonded forces every step
fullElectFrequency  2    ;# PME only every other step

# Constant Temperature Control
langevin            on            ;# langevin dynamics
langevinDamping     1.0            ;# damping coefficient of 1/ps

# Constant Pressure Control (variable volume)
useGroupPressure      yes ;# needed for rigidBonds
useFlexibleCell       no
useConstantArea       no

langevinPiston        on
langevinPistonTarget  1.01325 ;#  in bar -> 1 atm
langevinPistonPeriod  50.0
langevinPistonDecay   25.0
langevinPistonTemp    $temperature

{run}

exit
"""

prod_io = """
coordinates         mobley_{prefix}.pdb
bincoordinates      mobley_{prefix}_equil.coor
binvelocities       mobley_{prefix}_equil.vel
extendedsystem      mobley_{prefix}_equil.xsc
outputName          mobley_{prefix}_prod
"""

prod_run = """
{constraints}

langevinTemp $temperature

source               fep.tcl

alch                 on
alchType             fep
alchFile             mobley_{prefix}.pdb
alchCol              B
alchOutFreq          50
alchOutFile          mobley_{prefix}_{mode}.fepout

alchVdwLambdaEnd     1.0
alchElecLambdaStart  0.5
alchVdWShiftCoeff    5.0
alchDecouple         ON

alchEquilSteps       100000
set nSteps           1250000

runFEP         {start} {end} {step}      $nSteps
"""

constraints_template = """
# CONSTRAINTS
fixedAtoms          on
fixedAtomsFile      mobley_{prefix}.pdb
fixedAtomsCol       B
"""

gpu_template = """
usePMECUDA on
SOAintegrate on
CUDASOAintegrate on
alchPMECUDA on
bondedCUDA 255
"""

run_template = """#!/usr/bin/bash
#PBS -l walltime=12:00:00
#PBS -l mem=400Mb
#PBS -l ncpus=16
#PBS -j oe
set -e


# check if exists
cd "${{PBS_O_WORKDIR}}"

echo

echo hostname "$(hostname)"
echo nproc "$(nproc)"
lscpu | grep "Model name"

{run}
"""

input_list = """
mobley_1017962
"""
