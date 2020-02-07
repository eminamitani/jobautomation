from jobautomation import remote

with open('alldirs-2019-11-11.txt', 'r') as f:
    all=f.readlines()

dirs=[d.rstrip('\n') for d in all]

remote.removeFilesRCCS(dirs,['WAVECAR', 'CHG'])