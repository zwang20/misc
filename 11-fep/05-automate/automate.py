#!/usr/bin/python

import logging
import subprocess

import parmed as pmd

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

prefix = "mobley_1017962"
logger.info(f"Starting processing of {prefix}")

logger.debug("Creating directory")
subprocess.run(['mkdir', prefix]).check_returncode()

logger.info(f"Converting gro and top into pdb and psf")
gmx_top = pmd.load_file(f'FreeSolv/gromacs_solvated/{prefix}.top', xyz=f'FreeSolv/gromacs_solvated/{prefix}.gro')
gmx_top.save(f'{prefix}/{prefix}.psf')
gmx_top.save(f'{prefix}/{prefix}.pdb')

logger.info(f"Copying prm file")
subprocess.run(['cp', f'FreeSolv/charmm/{prefix}.prm', f'{prefix}/{prefix}.prm'])

run_template=f"""#!/bin/bash
#PBS -l walltime=00:10:00
#PBS -l mem=200Mb
#PBS -l ncpus=16
#PBS -j oe

# add modules
module purge
module add namd/3.0.1
module add tcl/8.6.12

# check if exists
[[ $PBS_O_WORKDIR ]] || {{ echo path does not exist; exit 1; }} && cd ${{PBS_O_WORKDIR}}

# print info
hostname
nproc
lscpu | grep "Model name"

# run program
#PATH="/srv/scratch/z5358697/namd:$PATH" namd3 +p$(nproc) equilibrate.namd
namd3 +p$(nproc) equilibrate.namd

# print cpuinfo
echo hostname $(hostname)
echo nproc $(nproc)
lscpu | grep "Model name"
# lscpu | grep "Model name" | cut -d : -f 2 | xargs

# TODO
# submit jobs for forwards and backwards
"""

with open(f"{prefix}/{prefix}_equilibrate", 'w') as f:
    f.write(run_template)

equilibrate_template = f"""
# Minimization and Equilibration

structure          {prefix}.psf
coordinates        {prefix}.pdb

outputname     methane_equilibrated

firsttimestep      0

# Input
paraTypeCharmm      on
parameters          par_all27_prot_lipid.inp
parameters          {prefix}.prm
temperature         298

# Force-Field Parameters
exclude             scaled1-4
1-4scaling          1.0
cutoff              12.0
switching           on
switchdist          10.0
pairlistdist        14.0


# Integrator Parameters
timestep            2.0
rigidBonds          all  ;# needed for 2fs steps
nonbondedFreq       1
fullElectFrequency  1
stepspercycle       10


# Constant Temperature Control
langevin            on   ;# do langevin dynamics
langevinDamping     1.0    ;# damping coefficient (gamma) of 1/ps
langevinTemp        298
langevinHydrogen    off  ;# don't couple langevin bath to hydrogens

langevinPiston        on
langevinPistonTarget  1.01325      ;# pressure in bar -> 1 atm
langevinPistonPeriod  100.         ;# oscillation period around 100 fs
langevinPistonDecay   50.          ;# oscillation decay time of 50 fs
langevinPistonTemp    298 ;# coupled to heat bath

#PME (for full-system periodic electrostatics)
PME                 yes
# let NAMD determine grid
PMEGridSpacing      1.0

outputEnergies      1000
outputpressure      1000
dcdfreq             1000
outputTiming        1000


# Repeating unit cells
# Periodic Boundary Conditions
cellBasisVector1    30.0    0.   0.0
cellBasisVector2     0.0  30.0   0.0
cellBasisVector3     0.0    0   30.0
cellOrigin          0.0   0.0  0.0

wrapAll             on
useGroupPressure      yes

# Minimization
minimize            1000
reinitvels          298
run 200000;
"""

with open(f"{prefix}/equilibrate.namd", 'w') as f:
    f.write(equilibrate_template)
