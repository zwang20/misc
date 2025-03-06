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

equil_run = """
foreach temp {30 60 90 120 150 180 210 240 270 300} dur {25000 25000 25000 25000 25000 50000 50000 50000 50000 1000000} {
    print "Running $dur steps at $temp kelvin."
    langevinTemp $temp
    run $dur
}
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

prep_run = """
PATH="/srv/scratch/z5358697/namd:$PATH" namd3 "+p$(nproc)" mobley_{prefix}_min.namd
PATH="/srv/scratch/z5358697/namd:$PATH" namd3 "+p$(nproc)" mobley_{prefix}_equil.namd
cd ..
cd fw0
cp ../prep/mobley_{prefix}_equil.coor .
cp ../prep/mobley_{prefix}_equil.vel  .
cp ../prep/mobley_{prefix}_equil.xsc  .
qsub {prefix}_fw0
cd ..
cd fw1
cp ../prep/mobley_{prefix}_equil.coor .
cp ../prep/mobley_{prefix}_equil.vel  .
cp ../prep/mobley_{prefix}_equil.xsc  .
qsub {prefix}_fw1
cd ..
cd bw0
cp ../prep/mobley_{prefix}_equil.coor .
cp ../prep/mobley_{prefix}_equil.vel  .
cp ../prep/mobley_{prefix}_equil.xsc  .
qsub {prefix}_bw0
cd ..
cd bw1
cp ../prep/mobley_{prefix}_equil.coor .
cp ../prep/mobley_{prefix}_equil.vel  .
cp ../prep/mobley_{prefix}_equil.xsc  .
qsub {prefix}_bw1
cd ..
cd fwf0
cp ../prep/mobley_{prefix}_equil.coor .
cp ../prep/mobley_{prefix}_equil.vel  .
cp ../prep/mobley_{prefix}_equil.xsc  .
qsub {prefix}_fwf0
cd ..
cd fwf1
cp ../prep/mobley_{prefix}_equil.coor .
cp ../prep/mobley_{prefix}_equil.vel  .
cp ../prep/mobley_{prefix}_equil.xsc  .
qsub {prefix}_fwf1
cd ..
cd bwf0
cp ../prep/mobley_{prefix}_equil.coor .
cp ../prep/mobley_{prefix}_equil.vel  .
cp ../prep/mobley_{prefix}_equil.xsc  .
qsub {prefix}_bwf0
cd ..
cd bwf1
cp ../prep/mobley_{prefix}_equil.coor .
cp ../prep/mobley_{prefix}_equil.vel  .
cp ../prep/mobley_{prefix}_equil.xsc  .
qsub {prefix}_bwf1
cd ..

"""

# loop over output
with open("output.txt") as input_file:
    for input_line in input_file:
        prefix = input_line.strip().split(" ", 1)[0].strip().split("_")[1]
        print(prefix)
        os.makedirs(prefix, exist_ok=True)
        os.chdir(prefix)

        # copy mol2 file here
        os.system(f"cp ../FreeSolv/mol2files_gaff/mobley_{prefix}.mol2 .")

        os.system(f"cp ../fep.tcl .")

        # generate leap.in
        with open("leap.in", "w") as f:
            f.write(tleap_template.format(prefix=prefix))

        # solvate molecule
        os.system(f"tleap -s -f leap.in")

        # add beta to molecule
        subprocess.run(
            [
                "sed",
                "-i",
                "/MOL/s/1\\.00  0\\.00/1.00  1.00/g",
                f"mobley_{prefix}.pdb",
            ]
        )

        # get size
        with open(f"mobley_{prefix}.pdb") as f:
            x, y, z = map(float, f.readline().split(maxsplit=4)[1:4])
            print(x, y, z)

        # generate prepare sequence
        os.makedirs("prep", exist_ok=True)
        os.chdir("prep")
        os.system(f"cp ../mobley_{prefix}.prmtop .")
        os.system(f"cp ../mobley_{prefix}.pdb .")

        # make namd configs
        with open(f"mobley_{prefix}_min.namd", "w") as f:
            f.write(
                generic_template.format(
                    io=min_io.format(prefix=prefix),
                    x=x,
                    y=y,
                    z=z,
                    run="langevinTemp $temperature\nminimize 2000",
                    prefix=prefix,
                )
            )

        with open(f"mobley_{prefix}_equil.namd", "w") as f:
            f.write(
                generic_template.format(
                    io=equil_io.format(prefix=prefix),
                    run=equil_run,
                    x=x,
                    y=y,
                    z=z,
                    prefix=prefix,
                )
            )

        with open(f"{prefix}_prep", "w") as f:
            f.write(run_template.format(run=prep_run.format(prefix=prefix)))

        os.chdir("..")

        for mode in ["fw0", "fw1", "bw0", "bw1", "fwf0", "fwf1", "bwf0", "bwf1"]:
            print(mode)
            os.makedirs(mode, exist_ok=True)
            os.chdir(mode)
            os.system(f"cp ../mobley_{prefix}.prmtop .")
            os.system(f"cp ../mobley_{prefix}.pdb .")
            os.system(f"cp ../fep.tcl .")

            # check if frozen
            if mode[2] == "f":
                constraints = constraints_template.format(prefix=prefix)
            else:
                constraints = ""

            # generate start end and step
            if mode[0] == "f":
                if mode[-1] == "0":
                    start, end, step = 0.0, 0.5, 0.05
                elif mode[-1] == "1":
                    start, end, step = 0.5, 1.0, 0.05
                else:
                    print(mode[-1])
                    assert False
            elif mode[0] == "b":
                if mode[-1] == "0":
                    start, end, step = 1.0, 0.5, -0.05
                elif mode[-1] == "1":
                    start, end, step = 0.5, 0.0, -0.05
                else:
                    print(mode[-1])
                    assert False
            else:
                print(mode[0])
                assert False

            with open(f"{prefix}_{mode}", "w") as f:
                f.write(
                    run_template.format(
                        run=f'PATH="/srv/scratch/z5358697/namd:$PATH" namd3 "+p$(nproc)" mobley_{prefix}_{mode}.namd'
                    )
                )

            with open(f"mobley_{prefix}_{mode}.namd", "w") as f:
                f.write(
                    generic_template.format(
                        io=prod_io.format(prefix=prefix),
                        prefix=prefix,
                        x=x,
                        y=y,
                        z=z,
                        run=prod_run.format(
                            prefix=prefix,
                            mode=mode,
                            constraints=constraints,
                            start=start,
                            end=end,
                            step=step,
                        ),
                    )
                )

            os.chdir("..")
        os.chdir("..")
