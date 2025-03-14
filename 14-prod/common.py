import subprocess


def get_previous_files():
    return (
        subprocess.run(["ls", "batch"], capture_output=True, check=True)
        .stdout.decode("utf-8")
        .strip()
        .split()
    )


def get_batch_number() -> int:
    return int(get_previous_files()[-1].split(".")[0])


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

equil_run = """
foreach temp {30 60 90 120 150 180 210 240 270 300} dur {100000 100000 100000 100000 100000 100000 100000 100000 100000 1000000} {
    print "Running $dur steps at $temp kelvin."
    langevinTemp $temp
    run $dur
}
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

tleap_template = """
source leaprc.gaff2
source leaprc.water.tip3p
mol = loadMol2 qm_{prefix}.mol2
check mol
solvatebox mol TIP3PBOX {size}
check mol
savepdb mol mobley_{prefix}.pdb
saveamberparm mol mobley_{prefix}.prmtop mobley_{prefix}.inpcrd
quit
"""
