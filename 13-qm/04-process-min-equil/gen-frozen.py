#!/usr/bin/python

import subprocess, os
from common import prefix_list, skip_list

prod_io = """
coordinates         mobley_{prefix}.pdb
bincoordinates      mobley_{prefix}_equil.coor
binvelocities       mobley_{prefix}_equil.vel
extendedsystem      mobley_{prefix}_equil.xsc
outputName          mobley_{prefix}_prod
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

runFEP         {start} {end} {step}      $nSteps
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
margin              2.0

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

# CONSTRAINTS
fixedAtoms          on
fixedAtomsFile      mobley_{prefix}.pdb
fixedAtomsCol       B

{run}

exit
"""

run_template = f"""#!/usr/bin/bash
#PBS -l walltime=12:00:00
#PBS -l mem=1Gb
#PBS -l ncpus=16
#PBS -l select=cpuflags=avx512_vpopcntdq
#PBS -j oe
#PBS -J 0-{len(prefix_list)*2 - 1}
set -e


# check if exists
cd "${{PBS_O_WORKDIR}}/${{PBS_ARRAY_INDEX}}"

echo

echo hostname "$(hostname)"
echo nproc "$(nproc)"
lscpu | grep "Model name"

PATH="/srv/scratch/z5358697/namd_avx512:$PATH" namd3 "+p$(nproc)" frozen.namd
"""

for index, prefix in enumerate(prefix_list):
    if prefix in skip_list:
        continue
    for i in range(index, len(prefix_list) + 1 + index, len(prefix_list)):

        print(i, prefix)

        # check if exit successful
        subprocess.run(
            [
                "grep",
                "-F",
                "Job execution was successful. Exit Status 0.",
                f"min-equil/qm-min-equil.o6296139.{index}",
            ],
            capture_output=True,
        ).check_returncode()

        # make output directory
        os.makedirs(f"frozen/{i}", exist_ok=True)

        # copy input files
        subprocess.run(["cp", "fep.tcl", f"frozen/{i}/"]).check_returncode()
        subprocess.run(["cp", f"min-equil/{index}/mobley_{prefix}.pdb", f"frozen/{i}/"])
        subprocess.run(
            ["cp", f"min-equil/{index}/mobley_{prefix}.prmtop", f"frozen/{i}/"]
        ).check_returncode()
        subprocess.run(
            ["cp", f"min-equil/{index}/mobley_{prefix}_equil.coor", f"frozen/{i}/"]
        ).check_returncode()
        subprocess.run(
            ["cp", f"min-equil/{index}/mobley_{prefix}_equil.vel", f"frozen/{i}/"]
        ).check_returncode()
        subprocess.run(
            ["cp", f"min-equil/{index}/mobley_{prefix}_equil.xsc", f"frozen/{i}/"]
        ).check_returncode()

        # get size
        with open(f"frozen/{i}/mobley_{prefix}.pdb") as f:
            x, y, z = map(float, f.readline().split(maxsplit=4)[1:4])
            print(x, y, z)

        # generate constants
        if i < len(prefix_list):  # forward
            start = 0
            end = 1
            step = 0.05
        else:
            start = 1
            end = 0
            step = -0.05

        assert step != 0
        if step > 0:
            assert 0 <= start < end <= 1
        else:
            assert 1 >= start > end >= 0

        # write namd
        with open(f"frozen/{i}/frozen.namd", "w") as f:
            f.write(
                generic_template.format(
                    io=prod_io.format(prefix=prefix),
                    prefix=prefix,
                    x=x,
                    y=y,
                    z=z,
                    run=prod_run.format(
                        prefix=prefix,
                        mode=i,
                        start=start,
                        end=end,
                        step=step,
                    ),
                )
            )

# write array job file
with open(f"frozen/frozen", "w") as f:
    f.write(run_template)
print(len(prefix_list))
