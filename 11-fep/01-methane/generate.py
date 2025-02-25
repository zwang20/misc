#!/usr/bin/python
import math
import os
import logging
import sys
import subprocess

# maximum = 2.0
step_time = 2.0
damping = 1.0
folder_prefix = "methane"
temperature = 298

time_ns_list = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000]
time_ns_list = [1]
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)


# loop over all times
for time_ns in time_ns_list:
    logger.info(f"Processing {time_ns=}")
    logger.debug(f"{step_time=}fs")

    steps = int(time_ns * 1000 // step_time)

    logger.debug(f"{steps=}")

    dcd = math.ceil(steps / 200)

    logger.debug(f"{dcd=}")

    walltime = math.ceil(steps / 40000)
    logger.info(f"Estimated walltime is {walltime} min")
    if walltime > 720:
        logger.error("Walltime exceeds allowed")
        sys.exit(1)
    logger.debug("Doubling walltime")
    walltime *= 2
    if walltime > 720:
        logger.warn("Double walltime exceeds allowance, cutting down")
        walltime = 720
    elif walltime < 10:
        logger.info("walltime below 10 mins, extending")
        walltime = 10
    walltime_string = f"{walltime // 60:02d}:{walltime % 60:02d}"
    logger.debug(f"{walltime_string=}")

    logger.debug("creating directory")
    subprocess.run(["mkdir", "-p", f"{folder_prefix}/{folder_prefix}_{time_ns}"]).check_returncode()

    logger.debug("copying files")
    subprocess.run(["cp", "methane.pdb", f"{folder_prefix}/{folder_prefix}_{time_ns}/methane.pdb"]).check_returncode()
    subprocess.run(["cp", "methane.psf", f"{folder_prefix}/{folder_prefix}_{time_ns}/methane.psf"]).check_returncode()
    subprocess.run(["cp", "par_all27_prot_lipid.inp", f"{folder_prefix}/{folder_prefix}_{time_ns}/par_all27_prot_lipid.inp"]).check_returncode()

    run_template = f"""#!/bin/bash
#PBS -l walltime={walltime_string}:00
#PBS -l mem=200Mb
#PBS -l ncpus=16
#PBS -j oe

# add modules
module purge
module add namd/3.0.1

# check if exists
[[ $PBS_O_WORKDIR ]] || {{ echo path does not exist; exit 1; }} && cd ${{PBS_O_WORKDIR}}

# delete previous
rm output.*

# print info
hostname
nproc
lscpu | grep "Model name"

# run program
namd3 +p$(nproc) methane.namd

# print cpuinfo
echo hostname $(hostname)
hostname
nproc
lscpu | grep "Model name"
"""

    with open(f"{folder_prefix}/{folder_prefix}_{time_ns}/{folder_prefix}_{time_ns}", "w") as f:
        f.write(run_template)

    namd_template = f"""
# Minimization and Equilibration

structure          methane.psf
coordinates        methane.pdb

set outputname     output

firsttimestep      0

#############################################################
## SIMULATION PARAMETERS                                   ##
#############################################################

# Input
paraTypeCharmm      on
parameters          par_all27_prot_lipid.inp
temperature         {temperature}


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
langevinTemp        {temperature}
langevinHydrogen    off  ;# don't couple langevin bath to hydrogens

#tCouple on
#tCoupleTemp {temperature}

langevinPiston        on
langevinPistonTarget  1.01325      ;# pressure in bar -> 1 atm
langevinPistonPeriod  100.         ;# oscillation period around 100 fs
langevinPistonDecay   50.          ;# oscillation decay time of 50 fs
langevinPistonTemp    {temperature} ;# coupled to heat bath


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

restartfreq         500
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
minimize            1000
reinitvels          {temperature}

run {steps};
"""

    logger.debug("writing .namd")
    with open(f"{folder_prefix}/{folder_prefix}_{time_ns}/methane.namd", "w") as f:
        f.write(namd_template)

logger.info("writing sub script")
with open(f"{folder_prefix}/sub.sh", "w") as f:
    f.write("#!/usr/bin/bash\n")
    for x in time_ns_list:
        f.write(f"cd {folder_prefix}_{x} && {{ qsub {folder_prefix}_{x}; cd ..; }}\n")
    os.system(f"chmod +x {folder_prefix}/sub.sh")
