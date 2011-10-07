import logging, os, datetime, sys
import glob, tempfile, subprocess
import paramiko
from OpenMesher.interfaces import IOpenMesherDeployPlugin
from OpenMesher.lib import *

class SSHDeploy(IOpenMesherDeployPlugin):
    def setupargs(self, parser):
        parser.add_argument('--deploy', action='store_true', help='Attempt to deploy the files to the routers (will not install or restart services)')
        parser.add_argument('--deploy-username', action='store', help='Username to use when deploying via SSH')
        parser.add_argument('--deploy-dir', action='store', help='Path to upload files')
    
    def activate(self):
        pass
    
    def deploy(self, packagePlugins = None, cliargs = None, stoponfailure = False):
        if not cliargs.deploy:
            return
        
        username = cliargs.deploy_username or 'root'
        deploydir = cliargs.deploy_dir or '/root/'
        logging.info('Assembling files for deployment...')
        
        deploy_dict = {}
        for plugin in packagePlugins:
            logging.debug('Processing files files from plugin %s...' %(plugin))
            deploy_dict = nested_dict_merge(deploy_dict, plugin.packages())
        
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        
        for router in deploy_dict:
            logging.info('Connecting to %s...' %(router))
            
            local_file_path = deploy_dict[router]
            local_file_split = deploy_dict[router].split('/')
            local_file_name = local_file_split[len(local_file_split) - 1]
            
            fh = open(local_file_path)
            ssh.connect(router, username='root')
            sftp = ssh.open_sftp()
            remote_file_name = os.path.abspath('%s/%s' %(deploydir, local_file_name))
            logging.info('Deploying %s to %s...' %(local_file_name, remote_file_name))
            remote_file = sftp.file(remote_file_name, 'wb')
            remote_file.set_pipelined(True)
            logging.debug('Starting transfer of %s' %(local_file_name))
            remote_file.write(fh.read())
            logging.debug('Completed transfer of %s' %(local_file_name))
            sftp.close()
            logging.debug('Disconnected from %s' %(router))
            ssh.close()


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
    
    def canrestart(self):
        return False
    
    def canreboot(self):
        return False

