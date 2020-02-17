from ase import Atoms
from ase.io import read, write
import os
import numpy as np
import shutil
from jobautomation import remote

contcar=read('CONTCAR', format='vasp')

top=contcar.positions[-1,2]

topLayers=[]

templete=os.listdir('./templete-RCCS')

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

#for NO1 bridge
angle1=[60]
angle2=[0]

#for NO2 ontop
angle3=[60,90]
angle4=[0]

'''
cell=np.array([[5.0, 0.0, 0.0],
               [0.0, 5.0, 0.0],
               [0.0, 0.0, 5.0]])
'''
image=[]
dirs=[]


for phi in angle1:
    for theta in angle2:
        no1 = no_orig.copy()
        no1.rotate(phi, 'y', center=[0, 0, d / 2.0])
        no1.rotate(theta, 'z', center=[0, 0, d / 2.0])

        for phi2 in angle3:
            for theta2 in angle4:
                no2=no_orig.copy()
                no2.rotate(phi2, 'y', center=[0,0,d/2.0])
                no2.rotate(theta2, 'z',center=[0,0,d/2.0])


                #for center ontop
                dist=2.2

                ontopNO=no2.copy()
                ontopNO.translate(ontopnext)
                ontopNO.translate([0.0,0.0,dist])

                #for bridge
                dist=1.8
                bridgeNO=no1.copy()
                bridgeNO.translate(bridge)
                bridgeNO.translate([0.0,0.0,dist])

                Surf=contcar.copy()
                Surf.extend(ontopNO)

                Surf.extend(bridgeNO)

                image.append(Surf)


                dirname="upper-ontop-angle1-"+str(phi)+"-"+str(theta)+"-angle2-"+str(phi2)+"-"+str(theta2)
                os.makedirs(dirname, exist_ok=True)
                dirs.append(dirname)


                write(dirname+"/POSCAR", Surf, format='vasp', vasp5=True, direct=True, sort=True)

                for file_name in templete:
                    full_file_name = os.path.join('./templete-RCCS', file_name)
                    if (os.path.isfile(full_file_name)):
                        target_file_name = os.path.join(dirname, file_name)
                        shutil.copy(full_file_name, target_file_name)

vaspfiles=os.listdir(dirs[0])
print(vaspfiles)
workingdir='/lustre/home/users/brx/NO-Au111-search/'
remote.sendDirsToRCCS(dirs=dirs,vaspfiles=vaspfiles,workingdir=workingdir)