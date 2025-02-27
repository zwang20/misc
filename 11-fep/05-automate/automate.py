#!/usr/bin/python

import logging
import subprocess
import sys
import parmed as pmd

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if len(sys.argv) != 2:
    logger.critical(f"incorrect number of arguments {sys.argv}")
    sys.exit(1)

prefix = sys.argv[1]
logger.info(f"Starting processing of {prefix}")

logger.debug("Creating directory")
subprocess.run(["mkdir", prefix]).check_returncode()

logger.info(f"Converting gro and top into pdb and psf")
gmx_top = pmd.load_file(
    f"FreeSolv/gromacs_solvated/mobley_{prefix}.top",
    xyz=f"FreeSolv/gromacs_solvated/mobley_{prefix}.gro",
)
gmx_top.save(f"{prefix}/mobley_{prefix}.psf")
gmx_top.save(f"{prefix}/mobley_{prefix}.pdb")

logger.info(f"Copying prm file")
subprocess.run(
    ["cp", f"FreeSolv/charmm/mobley_{prefix}.prm", f"{prefix}/mobley_{prefix}.prm"]
).check_returncode()

logger.info(f"Fixing mobley_{prefix}.psf")
subprocess.run(
    ["sed", "-i", f"4 c \\ REMARKS mobley_{prefix}/", f"{prefix}/mobley_{prefix}.psf"]
)

logger.info(f"Fixing mobley_{prefix}.pdb")
subprocess.run(
    [
        "sed",
        "-i",
        "/W/!s/0\\.00  \\+0\\.00/0.00  1.00/g",
        f"{prefix}/mobley_{prefix}.pdb",
    ]
)

logger.info("Reading coordinates")
with open(f"{prefix}/mobley_{prefix}.pdb") as f:
    line = f.readline()
    origin_x, origin_y, origin_z, length_x, length_y, length_z = map(
        float, line.split()[1:7]
    )

run_template = f"""#!/bin/bash
#PBS -l walltime=01:00:00
#PBS -l mem=400Mb
#PBS -l ncpus=16
#PBS -j oe

# add modules
#module purge
#module add namd/3.0.1
#module add tcl/8.6.12

# check if exists
[[ $PBS_O_WORKDIR ]] || {{ echo path does not exist; exit 1; }} && cd ${{PBS_O_WORKDIR}}

echo

echo hostname $(hostname)
echo nproc $(nproc)
lscpu | grep "Model name"
"""

with open(f"{prefix}/{prefix}_equilibrate", "w") as f:
    f.write(run_template)
    f.write(
        'PATH="/srv/scratch/z5358697/namd:$PATH" namd3 +p$(nproc) equilibrate.namd > /dev/null || exit 2\n'
    )
    f.write(f"qsub {prefix}_forwards\n")
    f.write(f"qsub {prefix}_backwards\n")
with open(f"{prefix}/{prefix}_forwards", "w") as f:
    f.write(run_template)
    f.write(
        'PATH="/srv/scratch/z5358697/namd:$PATH" namd3 +p$(nproc) forwards.namd > /dev/null \n'
    )
with open(f"{prefix}/{prefix}_backwards", "w") as f:
    f.write(run_template)
    f.write(
        'PATH="/srv/scratch/z5358697/namd:$PATH" namd3 +p$(nproc) backwards.namd > /dev/null \n'
    )
equilibrate_template = f"""
# Minimization and Equilibration

structure          mobley_{prefix}.psf
coordinates        mobley_{prefix}.pdb

outputname         mobley_{prefix}_equilibrated

firsttimestep      0

# Input
paraTypeCharmm      on
parameters          ../common/par_all27_prot_lipid.inp
parameters          mobley_{prefix}.prm
temperature         298

# Force-Field Parameters
exclude             scaled1-4
1-4scaling          1.0
cutoff              12.0
switching           on
switchdist          10.0
pairlistdist        14.0


# Integrator Parameters
timestep            1.0
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
cellBasisVector1    {length_x}    0.0   0.0
cellBasisVector2     0.0  {length_y}   0.0
cellBasisVector3     0.0    0.0   {length_z}
cellOrigin         {origin_x} {origin_y} {origin_z}

wrapAll             on
useGroupPressure      yes
margin 8
minimize            10000
reinitvels          298
run 100000;
"""

logger.info("Writing equilibrate.namd")
with open(f"{prefix}/equilibrate.namd", "w") as f:
    f.write(equilibrate_template)


fep_template = f"""
structure          mobley_{prefix}.psf
coordinates         mobley_{prefix}.pdb

bincoordinates          mobley_{prefix}_equilibrated.coor
binvelocities           mobley_{prefix}_equilibrated.vel

extendedSystem          mobley_{prefix}_equilibrated.xsc

paraTypeCharmm      on
parameters          ../common/par_all27_prot_lipid.inp
parameters          mobley_{prefix}.prm

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

#tCouple on
#tCoupleTemp 298

langevinPiston        on
langevinPistonTarget  1.01325      ;# pressure in bar -> 1 atm
langevinPistonPeriod  100.         ;# oscillation period around 100 fs
langevinPistonDecay   50.          ;# oscillation decay time of 50 fs
langevinPistonTemp    298 ;# coupled to heat bath


# Electrostatic Force Evaluation
#MSM                 on
#MSMGridSpacing      2.5  ;# very sensitive to performance, use this default
#MSMxmin            -5.0
#MSMxmax             60.0
#MSMymin            -5.0
#MSMymax             60.0
#MSMzmin            -15.0
#MSMzmax             46

#PME (for full-system periodic electrostatics)
PME                 yes
PMETolerance            10e-6
PMEInterpOrder          4
# let NAMD determine grid
PMEGridSpacing      1.0


#restartfreq         500
outputEnergies      500
outputpressure      500
dcdfreq             500
outputTiming        500


#############################################################
## EXTRA PARAMETERS                                        ##
#############################################################

# Repeating unit cells

# Periodic Boundary Conditions
cellBasisVector1    {length_x}    0.0   0.0
cellBasisVector2     0.0  {length_y}   0.0
cellBasisVector3     0.0    0.0   {length_z}
cellOrigin         {origin_x} {origin_y} {origin_z}

wrapAll             on
useGroupPressure      yes
margin 8

#############################################################
## EXECUTION SCRIPT                                        ##
#############################################################

# FEP

source                  ../common/fep.tcl

alch                    on
alchType                FEP
alchFile                mobley_{prefix}.pdb
alchCol                 B
alchOutFreq             10

alchVdwLambdaEnd        1.0
alchElecLambdaStart     0.5
alchVdWShiftCoeff       6.0
alchDecouple            no

alchEquilSteps          1000
set numSteps            5000
"""

logger.info("Writing forwards and backwards config")
with open(f"{prefix}/forwards.namd", "w") as f:
    f.write(fep_template)
    f.write(f"outputName mobley_{prefix}_forwards\n")
    f.write(f"alchOutFile             mobley_{prefix}_forwards.fepout\n")
    f.write("runFEP 0.0 1.0 0.0625 $numSteps\n")
with open(f"{prefix}/backwards.namd", "w") as f:
    f.write(fep_template)
    f.write(f"outputName mobley_{prefix}_backwards\n")
    f.write(f"alchOutFile             mobley_{prefix}_backwards.fepout\n")
    f.write("runFEP 1.0 0.0 -0.0625 $numSteps")
