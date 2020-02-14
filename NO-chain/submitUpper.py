from jobautomation import remote

with open('alldirs-2020-02-14.txt', 'r') as f:
    all=f.readlines()

dirs=[d.rstrip('\n') for d in all]

remote.jobSubmitRCCS(dirs)