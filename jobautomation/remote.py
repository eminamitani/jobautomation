from ase.build import fcc111
from ase import Atoms
from ase.io import read, write
from ase.constraints import FixAtoms
import paramiko
import os
from getpass import getpass
import datetime
import math

#send several directlies at one time, avoid typing passphrase so many times...
def sendDirsToIMR(dirs, vaspfiles):

    print("type your passwd for IMR supercomputer node")
    passwd = getpass()
    config_file = os.path.join(os.getenv('HOME'), '.ssh/config')
    ssh_config = paramiko.SSHConfig()
    ssh_config.parse(open(config_file, 'r'))
    lkup = ssh_config.lookup('super.imr')

    # ProxyCommand setup
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()
    print("what found in config file")
    print(lkup)

    ssh.connect(
        lkup['hostname'],
        username=lkup['user'],
        sock=paramiko.ProxyCommand(lkup['proxycommand']),
        password=passwd
    )

    sftp = ssh.open_sftp()
    workingdir='/home/emi0716/work/'
    for i in dirs:
        mkdircommand='mkdir '+ workingdir+i
        stdin, stdout, stderr = ssh.exec_command(mkdircommand)
        outlines = stdout.readlines()
        result = ''.join(outlines)
        print(result)

    for i in dirs:

        #TODO catch stderr
        for f in vaspfiles:
            origin="./"+i+"/"+f
            print("origin:"+origin)
            #print(os.path.exists(origin))
            target=workingdir+i+"/"+f
            print("target:"+target)
            sftp.put(origin, target)

    with open("joblog-"+datetime.today+".txt", "w") as f:
        for i in dirs:
            f.write(str(workingdir+i)+'\n')


    sftp.close()
    ssh.close()

#send to RCCS supercomputer, RCCS do not need pass-phrase

def sendToRCCS(files,dir):
    config_file = os.path.join(os.getenv('HOME'), '.ssh/config')
    ssh_config = paramiko.SSHConfig()
    ssh_config.parse(open(config_file, 'r'))
    lkup = ssh_config.lookup('RCCCS')

    # ProxyCommand setup
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()
    print("what found in config file")
    print(lkup)

    ssh.connect(
        lkup['hostname'],
        username=lkup['user'],
        key_filename=lkup['identityfile'],
    )

    mkdircommand='mkdir '+dir
    stdin, stdout, stderr = ssh.exec_command(mkdircommand)

    #TODO catch stderr

    sftp = ssh.open_sftp()

    for f in files:
        target=dir+"/"+f
        sftp.put(f, target)

    sftp.close()
    ssh.close()

def sendDirsToRCCS(dirs, vaspfiles):

    config_file = os.path.join(os.getenv('HOME'), '.ssh/config')
    ssh_config = paramiko.SSHConfig()
    ssh_config.parse(open(config_file, 'r'))
    lkup = ssh_config.lookup('RCCS')

    # ProxyCommand setup
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()
    print("what found in config file")
    print(lkup)

    ssh.connect(
        lkup['hostname'],
        username=lkup['user'],
        key_filename=lkup['identityfile'],
    )

    sftp = ssh.open_sftp()
    workingdir='/lustre/home/users/brx/NO-Au111-search/'
    for i in dirs:
        mkdircommand='mkdir '+ workingdir+i
        stdin, stdout, stderr = ssh.exec_command(mkdircommand)
        outlines = stdout.readlines()
        result = ''.join(outlines)
        print(result)

    for i in dirs:

        #TODO catch stderr
        for f in vaspfiles:
            origin="./"+i+"/"+f
            print("origin:"+origin)
            #print(os.path.exists(origin))
            target=workingdir+i+"/"+f
            print("target:"+target)
            sftp.put(origin, target)

    with open("alldirs-"+str(datetime.date.today())+".txt", "w") as f:
        for i in dirs:
            f.write(str(workingdir+i)+'\n')


    sftp.close()

    ssh.close()

#automatic job submission in RCCS
def jobSubmitRCCS(dirs):

    config_file = os.path.join(os.getenv('HOME'), '.ssh/config')
    ssh_config = paramiko.SSHConfig()
    ssh_config.parse(open(config_file, 'r'))
    lkup = ssh_config.lookup('RCCS')

    # ProxyCommand setup
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()
    print("what found in config file")
    print(lkup)

    ssh.connect(
        lkup['hostname'],
        username=lkup['user'],
        key_filename=lkup['identityfile'],
    )

    jobcommand = "jsub -q PN run.sh"
    joblogfile='joblog-'+str(datetime.datetime.now())+'.txt'

    f=open(joblogfile,'w')

    for i in dirs:
        print(i)

        chdircommand="cd "+i

        stdin, stdout, stderr = ssh.exec_command(chdircommand+";"+"pwd;"+jobcommand)
        outlines = stdout.readlines()
        result = ''.join(outlines)
        err=stderr.readlines()
        print(result)
        print(err)

        f.write(result)

    f.flush()
    f.close()

def jobStateRCCS(log, reqfiles):
    config_file = os.path.join(os.getenv('HOME'), '.ssh/config')
    ssh_config = paramiko.SSHConfig()
    ssh_config.parse(open(config_file, 'r'))
    lkup = ssh_config.lookup('RCCS')

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()
    print("what found in config file")
    print(lkup)

    ssh.connect(
        lkup['hostname'],
        username=lkup['user'],
        key_filename=lkup['identityfile'],
    )

    sftp = ssh.open_sftp()

    jobstatusCommand="jobinfo -c -l -h cclx"

    finishedJobStatusCommand="jobeff -h cclx"

    runningJobID=[]

    stdin, stdout, stderr = ssh.exec_command(jobstatusCommand)
    outlines = stdout.readlines()
    #running = ''.join(outlines)
    #print('running job')
    #print(running)

    for l in outlines[3:-1]:
        #print(l.split())
        runningJobID.append(l.split()[1])

    #print(runningJobID)
    finishedJobID=[]
    stdin, stdout, stderr = ssh.exec_command(finishedJobStatusCommand)
    outlines = stdout.readlines()
    #finished = ''.join(outlines)
    #print('finished job')
    #print(finished)
    for l in outlines[4:-1]:
        #print(l.split('|'))
        finishedJobID.append(l.split('|')[0].lstrip())

    #print(finishedJobID)
    #parse log file
    jobinfo=[]
    with open(log,"r") as log:
        lines=log.readlines()

    jobnumber=len(lines)//2

    for i in range(jobnumber):
        info={'remote':lines[i*2].rstrip('\n'), 'ID':lines[i*2+1].split(".")[0]}
        jobinfo.append(info)

    print(jobinfo)

    lf=open("download"+str(datetime.datetime.now())+".txt",'w')

    for j in jobinfo:
        if j['ID'] in runningJobID:
            print(str(j['ID'])+" is still running or queuing")
        elif j['ID'] in finishedJobID:
            print(str(j['ID']) + " is finished")
            print("download files to local directory: ./"+str(os.path.basename(j['remote'])))
            local=os.path.basename(j['remote'])
            lf.write(str(local) +"\n")

            #download results
            for f in reqfiles:
                localfile=os.path.join(local,f)
                remotefile=os.path.join(j['remote'],f)
                #print(localfile)
                #print(remotefile)
                sftp.get(remotefile,localfile)


    sftp.close()
    ssh.close()

    lf.flush()
    lf.close()

#automatic job submission in IMR
def jobSubmitIMR(dirs):

    config_file = os.path.join(os.getenv('HOME'), '.ssh/config')
    ssh_config = paramiko.SSHConfig()
    ssh_config.parse(open(config_file, 'r'))
    lkup = ssh_config.lookup('super.imr')
    print("type your passwd for IMR supercomputer node")
    passwd = getpass()

    # ProxyCommand setup
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()
    print("what found in config file")
    print(lkup)

    ssh.connect(
        lkup['hostname'],
        username=lkup['user'],
        sock=paramiko.ProxyCommand(lkup['proxycommand']),
        password=passwd
    )

    jobcommand = "qsub run_imr.sh"
    joblogfile='joblog-'+str(datetime.datetime.now())+'.txt'

    f=open(joblogfile,'w')

    for i in dirs:
        print(i)

        chdircommand="cd "+i

        stdin, stdout, stderr = ssh.exec_command(chdircommand+";"+"pwd;"+jobcommand)
        outlines = stdout.readlines()
        result = ''.join(outlines)
        err=stderr.readlines()
        print(result)
        print(err)

        f.write(result)

    f.flush()
    f.close()

def jobStateIMR(log, reqfiles):
    config_file = os.path.join(os.getenv('HOME'), '.ssh/config')
    ssh_config = paramiko.SSHConfig()
    ssh_config.parse(open(config_file, 'r'))
    lkup = ssh_config.lookup('super.imr')
    print("type your passwd for IMR supercomputer node")
    passwd = getpass()

    # ProxyCommand setup
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.load_system_host_keys()
    print("what found in config file")
    print(lkup)

    ssh.connect(
        lkup['hostname'],
        username=lkup['user'],
        sock=paramiko.ProxyCommand(lkup['proxycommand']),
        password=passwd
    )

    sftp = ssh.open_sftp()

    jobstatusCommand="statj"

    finishedJobStatusCommand="statj -x"

    runningJobID=[]

    stdin, stdout, stderr = ssh.exec_command(jobstatusCommand)
    outlines = stdout.readlines()
    #running = ''.join(outlines)
    #print('running job')
    #print(running)

    for l in outlines[3:-1]:
        #print(l.split())
        runningJobID.append(l.split()[1])

    #print(runningJobID)
    finishedJobID=[]
    stdin, stdout, stderr = ssh.exec_command(finishedJobStatusCommand)
    outlines = stdout.readlines()
    #finished = ''.join(outlines)
    #print('finished job')
    #print(finished)
    for l in outlines[4:-1]:
        #print(l.split('|'))
        finishedJobID.append(l.split('|')[0].lstrip())

    #print(finishedJobID)
    #parse log file
    jobinfo=[]
    with open(log,"r") as log:
        lines=log.readlines()

    jobnumber=len(lines)//2

    for i in range(jobnumber):
        info={'remote':lines[i*2].rstrip('\n'), 'ID':lines[i*2+1].split(".")[0]}
        jobinfo.append(info)

    print(jobinfo)

    lf=open("download"+str(datetime.datetime.now())+".txt",'w')

    for j in jobinfo:
        if j['ID'] in runningJobID:
            print(str(j['ID'])+" is still running or queuing")
        elif j['ID'] in finishedJobID:
            print(str(j['ID']) + " is finished")
            print("download files to local directory: ./"+str(os.path.basename(j['remote'])))
            local=os.path.basename(j['remote'])
            lf.write(str(local) +"\n")

            #download results
            for f in reqfiles:
                localfile=os.path.join(local,f)
                remotefile=os.path.join(j['remote'],f)
                #print(localfile)
                #print(remotefile)
                sftp.get(remotefile,localfile)


    sftp.close()
    ssh.close()

    lf.flush()
    lf.close()
