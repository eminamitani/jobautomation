import os
import shutil
from jobautomation import remote, routine
from ase import Atoms
from ase.constraints import FixAtoms
from pprint import pprint

file='/Users/emi/PycharmProjects/jobautomation/test/alldirs-2019-11-11.txt-resuts.txt'
with open(file) as f:
    tmp=f.readlines()

datas=[]
for i in tmp:
    dict=eval(i)
    datas.append(dict)

#extract not converged structure
dirs=[]
for d in datas:
    if(d['finish'] == False):
        dirs.append(d['ID'])

print(dirs)

#reduce POTIM to fast convergence
for d in dirs:
    shutil.copy('./templete-third/INCAR',d+'/INCAR')

#upload to RCCS
vaspfiles=['POTCAR','POSCAR','INCAR','vdw_kernel.bindat','run.sh']
remote.sendDirsToRCCS(dirs,vaspfiles)