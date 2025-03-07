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
margin              8.0

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

run_template = """#!/usr/bin/bash
#PBS -l walltime=12:00:00
#PBS -l mem=500Mb
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
"""

# loop over output
with open("database.txt") as input_file:
    for input_line in input_file:
        if input_line.startswith("#"):
            continue
        prefix = input_line.strip().split(";", 1)[0].strip().split("_")[1]
        print(prefix)

        os.makedirs(prefix, exist_ok=True)
        os.chdir(prefix)

        # copy mol2 file here
        subprocess.run(
            ["cp", f"../FreeSolv/mol2files_gaff/mobley_{prefix}.mol2", "."]
        ).check_returncode()

        subprocess.run(["cp", "../fep.tcl", "."]).check_returncode()

        # generate leap.in
        with open("leap.in", "w") as f:
            f.write(tleap_template.format(prefix=prefix))

        # solvate molecule
        subprocess.run(["tleap", "-s", "-f", "leap.in"]).check_returncode()

        # add beta to molecule
        subprocess.run(
            [
                "sed",
                "-i",
                "/MOL/s/1\\.00  0\\.00/1.00  1.00/g",
                f"mobley_{prefix}.pdb",
            ]
        ).check_returncode()

        # get size
        with open(f"mobley_{prefix}.pdb") as f:
            x, y, z = map(float, f.readline().split(maxsplit=4)[1:4])
            print(x, y, z)

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
