#!/usr/bin/python
run_template = """#!/usr/bin/bash
#PBS -l walltime=12:00:00
#PBS -l mem=500Mb
#PBS -l ncpus=16
#PBS -j oe
#PBS -J 0-14
set -e

cd "${PBS_O_WORKDIR}/${PBS_ARRAY_INDEX}"

PATH="/srv/scratch/z5358697/namd:$PATH" namd3 "+p$(nproc)" min.namd
PATH="/srv/scratch/z5358697/namd:$PATH" namd3 "+p$(nproc)" equil.namd
"""
