#!/bin/bash
#PBS -l walltime=1:00:00
#PBS -l mem=800Mb
#PBS -l ncpus=4
#PBS -j oe
cd ${PBS_O_WORKDIR}
module purge
module load gromacs/2022.3
module load intel-mpi/2021.7.1
gmx_mpi bar -b 100 -f lambda_?/dhdl.xvg
