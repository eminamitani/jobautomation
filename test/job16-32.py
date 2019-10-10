from jobautomation import remote

with open('alldirs-2019-10-08.txt', 'r') as f:
    all=f.readlines()

dirs=[d.rstrip('\n') for d in all]
#print(dirs)

print(dirs[16:32])

remote.jobSubmitIMR(dirs[16:32])