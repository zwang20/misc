#!/usr/bin/bash
set -e
cd 3323117; qsub 3323117.gpu; qsub 3323117.frozen; cd .. 
cd 6239320; qsub 6239320.gpu; qsub 6239320.frozen; cd .. 
cd 1723043; qsub 1723043.gpu; qsub 1723043.frozen; cd .. 
cd 4039055; qsub 4039055.gpu; qsub 4039055.frozen; cd .. 
