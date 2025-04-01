#!/usr/bin/bash
#PBS -l walltime=12:00:00
#PBS -l mem=16Gb
#PBS -l ncpus=16
#PBS -l select=cpuflags=avx512_vpopcntdq
#PBS -j oe
set -e

lscpu

cd "${PBS_O_WORKDIR}"

module add crest

crest mobley_1929982.xyz --alpb water --chrg 0 --uhf 0 -T 16
