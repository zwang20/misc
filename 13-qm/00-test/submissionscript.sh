#!/bin/bash
#PBS -l walltime=00:20:00
#PBS -l mem=3000Mb
#PBS -l ncpus=8
#PBS -l file=2000Mb
#PBS -j oe
#PBS -m ae

cd $PBS_O_WORKDIR

module load gaussian/09-D.01

sg unsw -c g09 < methane.com > methane.log


