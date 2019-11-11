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

def get_summary(dirfile):
    file = dirfile
    with open(file) as f:
        dirs = [os.path.basename(tmp.rstrip('\n')) for tmp in f.readlines()]
        results = []
        for d in dirs:
            outcar = d + '/OUTCAR'
            contcar = read(d + '/CONTCAR', format='vasp')

            with open(outcar) as of:
                #whether the structure relaxation finished or not
                finish=False
                #store total energy information
                toten = []
                #store magnetization information
                magnetization = []
                datas = [tmp.rstrip('\n') for tmp in of.readlines()]
                for data in datas:
                    if 'free  energy   TOTEN' in data:
                        toten.append(data)
                    if 'number of electron' in data and 'magnetization' in data:
                        magnetization.append(data)
                    #structure optimization
                    if 'reached required accuracy' in data:
                        finish = True


                final = {'ID': d, 'energy': toten[-1].split()[-2], 'mag': magnetization[-1].split()[-1],
                         'structure': contcar, 'finish':finish}
                results.append(final)

        sorted_results = sorted(results, key=lambda x: x['energy'])

        summary_file_name=dirfile+"-resuts.txt"
        # just simple output
        with open(summary_file_name, 'w') as output:
            for s in sorted_results:
                output.write(str(s) + '\n')

        # making XDATCAR for quick look
        summarydir = dirfile.split(".")[0]+'summary'
        os.makedirs(summarydir, exist_ok=True)
        with open(summarydir + "/XDATCAR", 'w') as ox:
            ox.write(str(sorted_results[0]['structure'].symbols) + '\n')
            ox.write('1.0 \n')
            ox.write(str(sorted_results[0]['structure'].cell[0][0]) + "  0.000 0.000 \n")
            ox.write("0.000  " + str(sorted_results[0]['structure'].cell[1][1]) + " 0.000 \n")
            ox.write("0.000  0.0000  " + str(sorted_results[0]['structure'].cell[2][2]) + " \n")
            ox.write("Au   N    O \n ")
            ox.write("126   1   1 \n ")

            counter = 1
            for i in sorted_results:
                ox.write("Direct configuration= " + str(counter) + "\n")
                counter = counter + 1
                # print(counter)
                for p in i['structure'].get_scaled_positions():
                    ox.write(' '.join(str(s) for s in p) + "\n")

def backup_files(dirfile):
    file = dirfile
    with open(file) as f:
        dirs = [os.path.basename(tmp.rstrip('\n')) for tmp in f.readlines()]

    for d in dirs:
        print(d)
        poscar = d + '/POSCAR'
        outcar = d + '/OUTCAR'
        vaspdata = d + '/vasprun.xml'
        xdatcar = d + '/XDATCAR'
        contcar = d + '/CONTCAR'
        incar = d+ '/INCAR'

        count = count_iteration(d)
        if count!=None:
            now=count+1
            print(now)

            shutil.copy(poscar, d + '/POSCAR' + "." + str(now))
            shutil.copy(outcar, d + '/OUTCAR' + "." + str(now))
            shutil.copy(xdatcar, d + '/XDARCAR' + "." + str(now))
            shutil.copy(vaspdata, d + '/vasprun.xml' + "." + str(now))
            shutil.copy(incar, d + '/INCAR' + "." + str(now))
            shutil.copy(contcar, poscar)


        else:
            shutil.copy(poscar, d + '/POSCAR.0')
            shutil.copy(outcar, d + '/OUTCAR.0')
            shutil.copy(xdatcar, d + '/XDATCAR.0')
            shutil.copy(vaspdata, d + '/vasprun.xml.0')
            shutil.copy(incar, d + '/INCAR.0')
            shutil.copy(contcar, poscar)
            





