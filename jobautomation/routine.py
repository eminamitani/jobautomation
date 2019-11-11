import os
import glob
import shutil
from ase import Atoms
from ase.io import read, write
from jobautomation import remote


def count_iteration(dir):
    '''

    :param dir: directory to check the iteration number
    :return: iteretion
    '''

    #updated file:POSCAR, OUTCAR
    poscars=glob.glob(dir+'/POSCAR*')
    outcars=glob.glob(dir+'/OUTCAR*')


    positr=[]
    for pos in poscars:
        filename=os.path.basename(pos)
        prefix=filename.split('.')
        if( len(prefix) > 1):
            positr.append(int(prefix[-1]))

    outitr=[]
    for out in outcars:
        filename=os.path.basename(out)
        prefix=filename.split('.')
        if( len(prefix) > 1):
            outitr.append(int(prefix[-1]))

    positr.sort()
    outitr.sort()

    poslast=positr[-1]
    outlast=outitr[-1]

    if(poslast != outlast):
        print('something wrong in last update process')

    return poslast




