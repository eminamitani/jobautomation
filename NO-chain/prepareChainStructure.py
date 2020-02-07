from ase import Atoms
from ase.io import read, write
import os
import numpy as np
import shutil
from jobautomation import remote

contcar=read('CONTCAR', format='vasp')

top=contcar.positions[-1,2]

topLayers=[]

#determine ontop & bridge position
for _ in contcar.positions:
    if (abs(_[2]-top))  < 0.1 :
        topLayers.append(_)

'''
create bridge - ontop -bridge chain structure
'''

ontop=topLayers[0]

print("ontop site="+str(ontop))

next=[]

for _ in topLayers[1:]:
    if (abs(ontop[0]-_[0])) < 0.1:
        next=_
        break

bridge=(ontop+next)/2.0
print("bridge site="+str(bridge))
ontopnext=ontop+(next-ontop)*2.0

d=1.15
no_orig=Atoms('NO', positions=[[0,0,0],[0,0,d]])

#create directories for possible transrate, rotation and so on
#symmetry, off-symmetry case

angle1=[30,60,90]
angle2=[0,30]

'''
cell=np.array([[5.0, 0.0, 0.0],
               [0.0, 5.0, 0.0],
               [0.0, 0.0, 5.0]])
'''
image=[]
dirs=[]


for phi in angle1:
    for theta in angle2:
        no=no_orig.copy()
        no.rotate(phi, 'y', center=[0,0,d/2.0])
        no.rotate(theta, 'z',center=[0,0,d/2.0])

        '''
        no_print=no.copy()
        no_print.set_cell(cell, scale_atoms=False)
        print(no.positions)
        write(str(phi) + "-" + str(theta)+".vasp", no_print, format='vasp', vasp5=True, direct=True)
        '''

        #for center ontop
        dist=1.9

        ontopNO=no.copy()
        ontopNO.translate(ontopnext)
        ontopNO.translate([0.0,0.0,dist])

        #for bridge
        dist=1.8
        bridgeNO=no.copy()
        bridgeNO.translate(bridge)
        bridgeNO.translate([0.0,0.0,dist])

        Surf=contcar.copy()
        Surf.extend(ontopNO)

        Surf.extend(bridgeNO)

        image.append(Surf)


        dirname="angle-"+str(phi)+"-"+str(theta)
        os.makedirs(dirname, exist_ok=True)


        write(dirname+"/POSCAR", Surf, format='vasp', vasp5=True, direct=True)