#!/usr/bin/bash
#PBS -l walltime=12:00:00
#PBS -l mem=1Gb
#PBS -l ncpus=16
#PBS -l select=cpuflags=avx512f
#PBS -j oe
#PBS -J 0-1
set -e

cd "${PBS_O_WORKDIR}/${PBS_ARRAY_INDEX}"

echo hostname "$(hostname)"
echo nproc "$(nproc)"
lscpu | grep "Model name"
echo

PATH="/srv/scratch/z5358697/namd:$PATH" namd3 "+p$(nproc)" min.namd
PATH="/srv/scratch/z5358697/namd:$PATH" namd3 "+p$(nproc)" equil.namd
