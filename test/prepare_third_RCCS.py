import os
import shutil
from jobautomation import remote

file='alldirs-2019-11-06.txt'
with open(file) as f:
    dirs=[os.path.basename(tmp.rstrip('\n')) for tmp in f.readlines()]

#replace INCAR to use wavefunction + IBRION=1 + minor fix for vdW functional
for d in dirs:
    shutil.copy('./templete-second/INCAR',d+'/INCAR')


vaspfiles=['POTCAR','POSCAR','INCAR','vdw_kernel.bindat','run.sh']
remote.sendDirsToRCCS(dirs,vaspfiles)