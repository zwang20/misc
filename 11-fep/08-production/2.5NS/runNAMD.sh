#!/bin/bash
#PBS -l walltime=24:00:00
#PBS -l mem=32GB
#PBS -l ncpus=28
#PBS -l jobfs=10gb
#PBS -l software=namd
#PBS -l wd
#PBS -P cw7 
#PBS -q normalbw 
#PBS -l storage=scratch/cw7

module load openmpi
module load namd/2.14

mpirun -np $PBS_NCPUS namd2 min.conf > min.log
mpirun -np $PBS_NCPUS namd2 equil.conf > equil.log
mpirun -np $PBS_NCPUS namd2 prod.conf > prod.log


