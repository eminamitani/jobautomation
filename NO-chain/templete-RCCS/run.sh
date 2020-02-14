#!/bin/sh
#PBS -l select=4:ncpus=40:mpiprocs=40:ompthreads=1:jobtype=small
#PBS -l walltime=24:00:00
cd ${PBS_O_WORKDIR}
mpirun -np 160 ~/vasp-5.4.1-Hamadasan-vdw/vasp.5.4.1/bin/vasp_std  > NO_Au111.out
