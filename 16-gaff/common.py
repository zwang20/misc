import subprocess


def get_previous_files():
    return (
        subprocess.run(["ls", "batch"], capture_output=True, check=True)
        .stdout.decode("utf-8")
        .strip()
        .split()
    )


def get_batch_number():
    return get_previous_files()[-1].split(".")[0]


def get_prefix_list(batch):
    prefix_list = []
    with open(f"batch/{batch}.txt", encoding="utf-8") as f:
        for line in f:
            prefix_list.append(line.strip())
    return prefix_list


generic_template = """
{io}

set temperature     300  ;# target temperature used several times below

restartfreq         100000     ;# 1000 steps = every 1ps
dcdfreq             100000

outputEnergies      100000       ;# 100 steps = every 0.2 ps
outputpressure      100000
XSTFreq             100000

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
margin              {margin}

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

{constraints}

{run}

exit
"""


min_io = """
coordinates         mobley_{prefix}.pdb
outputName          mobley_{prefix}_min
temperature 300
"""

equil_io = """
coordinates         mobley_{prefix}.pdb
bincoordinates      mobley_{prefix}_min.coor
outputName          mobley_{prefix}_equil
temperature 300
"""

prod_io = """
coordinates         mobley_{prefix}.pdb
bincoordinates      mobley_{prefix}_equil.coor
binvelocities       mobley_{prefix}_equil.vel
extendedsystem      mobley_{prefix}_equil.xsc
outputName          mobley_{prefix}_prod
"""


min_run = """
langevinTemp $temperature

minimize 100000
"""

equil_run = """
foreach temp {30 60 90 120 150 180 210 240 270 300} dur {100000 100000 100000 100000 100000 100000 100000 100000 100000 1000000} {
    print "Running $dur steps at $temp kelvin."
    langevinTemp $temp
    run $dur
}
"""

prod_run = """
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
set nSteps           1500000
# set nSteps           2500000

runFEP         {start:.2f} {end:.2f} {step:.2f}      $nSteps
"""


tleap_template = """
source leaprc.gaff
source leaprc.water.tip3p
loadamberparams mobley_{prefix}.frcmod
mol = loadMol2 mobley_{prefix}.mol2
check mol
solvatebox mol TIP3PBOX {size}
check mol
savepdb mol mobley_{prefix}.pdb
saveamberparm mol mobley_{prefix}.prmtop mobley_{prefix}.inpcrd
quit
"""

constraint_frozen = """
# CONSTRAINTS
fixedAtoms          on
fixedAtomsFile      mobley_{prefix}.pdb
fixedAtomsCol       B
"""

constraint_gpu = """
GPUresident on
# GPUAtomMigration on
GPUForceTable on
"""

katana_min_equil_batch = """#!/usr/bin/bash
#PBS -l walltime=02:00:00
#PBS -l mem=1Gb
#PBS -l ncpus=16
#PBS -l select=cpuflags=avx512f
#PBS -j oe
#PBS -J 0-{length}
set -e

lscpu

cd "${{PBS_O_WORKDIR}}/${{PBS_ARRAY_INDEX}}"

/srv/scratch/${{USER}}/.namd/namd3 "+p$(nproc)" min.namd > min.log
/srv/scratch/${{USER}}/.namd/namd3 "+p$(nproc)" equil.namd > equil.log
"""

katana_min_equil = """#!/usr/bin/bash
#PBS -l walltime=02:00:00
#PBS -l mem=1Gb
#PBS -l ncpus=16
#PBS -l select=cpuflags=avx512f
#PBS -j oe
set -e

lscpu

cd "${{PBS_O_WORKDIR}}"

/srv/scratch/${{USER}}/.namd/namd3 "+p$(nproc)" min.namd > min.log
/srv/scratch/${{USER}}/.namd/namd3 "+p$(nproc)" equil.namd > equil.log
"""

gadi_min_equil = """#!/usr/bin/bash
#PBS -l walltime=48:00:00
#PBS -l ncpus=1
#PBS -l mem=4Gb
#PBS -j oe
#PBS -P cw7
#PBS -q {queue}
#PBS -l storage=scratch/cw7
#PBS -l wd

# https://opus.nci.org.au/spaces/Help/pages/236880320

set -e

lscpu

#module load openmpi
#module load namd/3.0

#mpirun -np $PBS_NCPUS namd3 min.namd > min.log
#mpirun -np $PBS_NCPUS namd3 equil.namd > equil.log

/scratch/cw7/mw7780/namd/namd3 min.namd > min.log
/scratch/cw7/mw7780/namd/namd3 equil.namd > equil.log
"""

katana_gpu_batch = """#!/usr/bin/bash
#PBS -l walltime=12:00:00
#PBS -l mem=1Gb
#PBS -l ncpus=12
#PBS -l ngpus=1
#PBS -j oe
#PBS -J {start}-{end}
set -e

lscpu

cd "${{PBS_O_WORKDIR}}/${{PBS_ARRAY_INDEX}}"

/srv/scratch/${{USER}}/.namd_cuda/namd3 "+p$(nproc)" prod.namd > prod.log
"""

katana_frozen_batch = """#!/usr/bin/bash
#PBS -l walltime=12:00:00
#PBS -l mem=1Gb
#PBS -l ncpus=16
#PBS -l select=cpuflags=avx512_vpopcntdq
#PBS -j oe
#PBS -J {start}-{end}
set -e

lscpu

cd "${{PBS_O_WORKDIR}}/${{PBS_ARRAY_INDEX}}"

/srv/scratch/${{USER}}/.namd_avx512/namd3 "+p$(nproc)" prod.namd > prod.log
"""
