#!/bin/bash
#PBS -l walltime=1:00:00
#PBS -l mem=800Mb
#PBS -l ncpus=4
#PBS -j oe

# add modules
#module purge
#module add namd/2.14

# run job
#cd ${PBS_O_WORKDIR} || exit 1

# delete previous
rm output.*

# run program
time nice -n 19 namd3 +p16 sodium.namd

# print cpuinfo
lscpu | grep "Model name"
