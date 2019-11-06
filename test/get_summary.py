import os
import shutil
from ase import Atoms
from ase.io import read, write
from jobautomation import remote

file='alldirs-2019-10-08.txt'
with open(file) as f:
    dirs=[os.path.basename(tmp.rstrip('\n')) for tmp in f.readlines()]

results=[]
for d in dirs:
    outcar=d+'/OUTCAR'
    contcar=read(d+'/CONTCAR', format='vasp')

    with open(outcar) as of:
        toten=[]
        magnetization=[]
        datas=[tmp.rstrip('\n') for tmp in of.readlines()]
        for data in datas:
            if 'free  energy   TOTEN' in data:
                toten.append(data)
            if 'number of electron' in data and 'magnetization' in data:
                magnetization.append(data)

        final={'ID':d,'energy':toten[-1].split()[-2],'mag':magnetization[-1].split()[-1], 'structure':contcar}
        results.append(final)

sorted_results=sorted(results, key=lambda x:x['energy'])


#just simple output
with open('resuts.txt','w') as output:
    for s in sorted_results:
        output.write(str(s)+'\n')

#making XDATCAR for quick look
summarydir='summary'
os.makedirs(summarydir,exist_ok=True)
with open(summarydir+"/XDATCAR", 'w') as ox:
    ox.write(str(sorted_results[0]['structure'].symbols) +'\n')
    ox.write('1.0 \n')
    ox.write(str(sorted_results[0]['structure'].cell[0][0])+"  0.000 0.000 \n")
    ox.write("0.000  "+str(sorted_results[0]['structure'].cell[1][1]) + " 0.000 \n")
    ox.write("0.000  0.0000  " + str(sorted_results[0]['structure'].cell[2][2]) + " \n")
    ox.write("Au   N    O \n ")
    ox.write("126   1   1 \n ")

    counter=1
    for i in sorted_results:
        ox.write("Direct configuration= "+str(counter) +"\n")
        counter=counter+1
        #print(counter)
        for p in i['structure'].get_scaled_positions():
            ox.write(' '.join(str(s) for s in p) +"\n")

'''
#update CONTCAR to POSCAR

counter='update_counter.txt'

for d in dirs:
    print(d)
    poscar = d + '/POSCAR'
    outcar = d+'/OUTCAR'
    vaspdata=d + '/vasprun.xml'
    xdatcar = d + '/XDATCAR'
    contcar= d + '/CONTCAR'

    if os.path.exists(d+counter):
        with open(d+counter,"r") as f:
            lines=f.read()
            count=int(f.read())

        shutil.copy(poscar, d+'/POSCAR'+"."+count)
        shutil.copy(outcar, d+'/OUTCAR' + "." + count)
        shutil.copy(xdatcar, d+'/XDARCAR' + "." + count)
        shutil.copy(vaspdata, d+'/vasprun.xml' + "." + count)
        shutil.copy(contcar, poscar)
        new=count+1

        lines=lines.replace(str(count),str(new))
        with open(counter,"w") as f:
            f.write(lines)
    else:
        count=1
        shutil.copy(poscar, d+'/POSCAR.0')
        shutil.copy(outcar, d+'/OUTCAR.0')
        shutil.copy(xdatcar, d+'/XDATCAR.0')
        shutil.copy(vaspdata,d+'/vasprun.xml.0')
        shutil.copy(contcar, poscar)

        with open(d+counter,"w") as f:
            f.write(str(count))

'''

#resubmit job to RCCS
#prepare run.sh for RCCS
for d in dirs:
    shutil.copy('./templete-RCCS/run.sh',d+'/run.sh')

#using lower energy 81~168 pattern
senddirs=[]
for res in sorted_results[80:]:
    senddirs.append(res['ID'])

print(senddirs)
vaspfiles=['POTCAR','POSCAR','INCAR','vdw_kernel.bindat','run.sh']

remote.sendDirsToRCCS(senddirs,vaspfiles)





















