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


ontop=topLayers[0]

print("ontop site="+str(ontop))

next=[]

for _ in topLayers[1:]:
    if (abs(ontop[0]-_[0])) < 0.1:
        next=_
        break

bridge=(ontop+next)/2.0
print("bridge site="+str(bridge))


d=1.15
no_orig=Atoms('NO', positions=[[0,0,0],[0,0,d]])

#create directories for possible transrate, rotation and so on
#symmetry, off-symmetry case

angle1=[30,60,90]
angle2=[0,30,60,90]
shift=[[0.0,0.0,0.0],[0.5,0.0,0.0],[0.0,0.5,0.0],[0.5,0.5,0.0],[-0.5,0.0,0.0],[0.0,-0.5,0.0],[-0.5,-0.5,0.0]]

'''
cell=np.array([[5.0, 0.0, 0.0],
               [0.0, 5.0, 0.0],
               [0.0, 0.0, 5.0]])
'''
image_ontop=[]
image_bridge=[]
dirs=[]

templete=os.listdir('./templete-imr')

for phi in angle1:
    for theta in angle2:
        for diff in shift:
            no=no_orig.copy()
            no.rotate(phi, 'y', center=[0,0,d/2.0])
            no.rotate(theta, 'z',center=[0,0,d/2.0])

            '''
            no_print=no.copy()
            no_print.set_cell(cell, scale_atoms=False)
            print(no.positions)
            write(str(phi) + "-" + str(theta)+".vasp", no_print, format='vasp', vasp5=True, direct=True)
            '''

            #for ontop
            dist=1.9

            ontopNO=no.copy()
            ontopNO.translate(ontop)
            ontopNO.translate([0.0,0.0,dist])
            ontopNO.translate(diff)

            #for bridge
            dist=1.8
            bridgeNO=no.copy()
            bridgeNO.translate(bridge)
            bridgeNO.translate([0.0,0.0,dist])
            bridgeNO.translate(diff)

            ontopSurf=contcar.copy()
            ontopSurf.extend(ontopNO)

            bridgeSurf=contcar.copy()
            bridgeSurf.extend(bridgeNO)

            image_ontop.append(ontopSurf)
            image_bridge.append(bridgeSurf)

            strdiff='-'.join(str(d) for d in diff)

            ontopdir="ontop-"+str(phi)+"-"+str(theta)+"-"+strdiff
            os.makedirs(ontopdir, exist_ok=True)
            dirs.append(ontopdir)

            bridgedir="bridge-"+str(phi)+"-"+str(theta)+"-"+strdiff
            os.makedirs(bridgedir, exist_ok=True)
            dirs.append(bridgedir)

            write(bridgedir+"/POSCAR", bridgeSurf, format='vasp', vasp5=True, direct=True)
            write(ontopdir+"/POSCAR", ontopSurf, format='vasp', vasp5=True, direct=True)

            #copy input files
            for file_name in templete:
                full_file_name = os.path.join('./templete-imr', file_name)
                if (os.path.isfile(full_file_name)):
                    target_file_name = os.path.join(ontopdir, file_name)
                    shutil.copy(full_file_name, target_file_name)

            for file_name in templete:
                full_file_name = os.path.join('./templete-imr', file_name)
                if (os.path.isfile(full_file_name)):
                    target_file_name = os.path.join(bridgedir, file_name)
                    shutil.copy(full_file_name, target_file_name)

vaspfiles=os.listdir(dirs[0])
print(vaspfiles)
remote.sendDirsToIMR(dirs=dirs,vaspfiles=vaspfiles)



#create XDATCAR file to quick-look
with open("XDATCAR", 'w') as ox:
    ox.write(str(image_ontop[0].symbols) +'\n')
    ox.write('1.0 \n')
    ox.write(str(image_ontop[0].cell[0][0])+"  0.000 0.000 \n")
    ox.write("0.000  "+str(image_ontop[0].cell[1][1]) + " 0.000 \n")
    ox.write("0.000  0.0000  " + str(image_ontop[0].cell[2][2]) + " \n")
    ox.write("Au   N    O \n ")
    ox.write("126   1   1 \n ")

    counter=1
    for i in image_ontop:
        ox.write("Direct configuration= "+str(counter) +"\n")
        counter=counter+1
        #print(counter)
        for p in i.get_scaled_positions():
            ox.write(' '.join(str(s) for s in p) +"\n")
    for i in image_bridge:
        ox.write("Direct configuration= "+str(counter) +"\n")
        counter=counter+1
        for p in i.get_scaled_positions():
            ox.write(' '.join(str(s) for s in p) +"\n")
