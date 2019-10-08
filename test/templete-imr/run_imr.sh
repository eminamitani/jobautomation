#!/bin/sh
#PBS -l select=4  
#PBS -q P_016 
#PBS -N NO-Au(111)
#PBS -l walltime=24:00:00 
cd ${PBS_O_WORKDIR} 
aprun -n 144  -N 36  -j 1 /work/app/VASP5/current/bin/vasp_std 
