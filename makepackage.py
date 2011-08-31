import glob, os, tempfile, subprocess, paramiko

def mkdirs(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == 17:
            pass
        else:
            raise

def package_generator(config):
    base_path = tempfile.mkdtemp(prefix='openmesher-')
    print 'Base path: %s' %(base_path)
    mkdirs(base_path)
    for router in config:
        router_path = os.path.abspath(base_path + '/' + router)
        mkdirs(router_path)
        for cfgfile in config[router]:
            cfgfile_path = os.path.abspath(router_path + '/' + cfgfile)
            fpath, fname = os.path.split(cfgfile_path)
            mkdirs(fpath)
            fh = open(cfgfile_path, 'w')
            fh.write(config[router][cfgfile])
            fh.close()
            if fname == 'rules':
                #Hack to make dpkg rules file executable
                os.chmod(cfgfile_path, 0744)
        print 'Building package for router: %s' %(router)
        sCMD = 'fakeroot debian/rules binary'
        process = subprocess.Popen(sCMD, shell=True, stdout=subprocess.PIPE, cwd=router_path)
        process.wait()
        if process.returncode != 0:
            raise Exception('Package generation failed in %s' %(base_path))
        
#        print 'Connecting to %s' %(router)
#        fh = open(base_path + '/' + router.lower().split('.')[0] + '.deb')
#        ssh = paramiko.SSHClient()
#        ssh.load_host_keys(os.path.expanduser(os.path.join("~", ".ssh", "known_hosts")))
#        ssh.connect(router.lower(), username='root')
#        sftp = ssh.open_sftp()
#        print 'Transferring deb...'
#        remote_file = sftp.file('/root/%s.deb' %(router.lower().split('.')[0]), "wb")
#        remote_file.set_pipelined(True)
#        remote_file.write(fh.read())
#        sftp.close()
#        ssh.close()
#        print 'Complete'

