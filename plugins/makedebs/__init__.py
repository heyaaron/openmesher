import logging, interfaces, os, datetime, sys
import glob, tempfile, subprocess
from lib import nested_dict_merge

def dump_config_files(base_path, files_dict):
            for router in files_dict:
                for cfgfile in files_dict[router]:
                    cfgfile_path = os.path.abspath(base_path + '/' + router + '/' + cfgfile)
                    #logging.debug('Creating file %s for router %s' %(cfgfile_path, router))
                    fpath, fname = os.path.split(cfgfile_path)
                    _mkdirs(fpath)
                    fh = open(cfgfile_path, 'w')
                    fh.write(files_dict[router][cfgfile])
                    fh.close()
                    if fname == 'rules' or fname == 'postinst':
                        #BUG: Hack to make dpkg rules file executable
                        os.chmod(cfgfile_path, 0744)

def _mkdirs(path):
    try:
        os.makedirs(path)
    except OSError as e:
        if e.errno == 17:
            pass
        else:
            raise


class MakeDEBs(interfaces.IOpenMesherPackagePlugin):
    def activate(self):
        self._register('makedebs/changelog.conf')
        self._register('makedebs/compat.conf')
        self._register('makedebs/control.conf')
        self._register('makedebs/rules.conf')
        self._register('makedebs/postinst.conf')
    
    def setupargs(self, parser):
        parser.add_argument('--dpkg-version', default='1.0', action='store', help='Version number of the deb to create')

    #BUG: Need to fix the plugin arch so services can pass their config dirs to the package generator
    def process(self, mesh, configPlugins = None, cliargs = None, include_dirs = ['openvpn', 'quagga', 'shorewall', 'mesh-reverse.db'], restart_services = ['openvpn', 'quagga', 'shorewall']):
        base_path = tempfile.mkdtemp(prefix='openmesher-')
        logging.info('Base path: %s' %(base_path))
        _mkdirs(base_path)
        
        logging.debug('Generating control files for package...')
        
        for router in mesh.routers:
            self._files[router] = {}
            changelog_date = datetime.datetime.strftime(datetime.datetime.now(), '%A, %d %B %Y %H:%M:%S -0800')
            
            #BUG: %z doesn't work for some dumb reason: http://www.aczoom.com/blog/ac/2007-02-24/strftime-in-python
            # changelog_date = datetime.datetime.strftime(datetime.datetime.utcnow(), '%A, %d %B %Y %H:%M:%S +%z')
            self._files[router]['/debian/changelog'] = self._templates['makedebs/changelog.conf'].render(
                hostname=mesh.routers[router].hostname.lower(),
                package_version = cliargs.dpkg_version,
                changelog_date = changelog_date,
            )
            
            self._files[router]['/debian/compat'] = self._templates['makedebs/compat.conf'].render()
            
            self._files[router]['/debian/control'] = self._templates['makedebs/control.conf'].render(
                hostname = mesh.routers[router].hostname.lower(),
                fqdn = mesh.routers[router].fqdn,
                changelog_date = changelog_date,
            )
            
            #BUG: Need to figure out which files need to be installed / services restarted from various plugins
            self._files[router]['/debian/rules'] = self._templates['makedebs/rules.conf'].render(
                hostname = mesh.routers[router].hostname.lower(),
                dirs = include_dirs,
            )
            
            self._files[router]['/debian/postinst'] = self._templates['makedebs/postinst.conf'].render(
                restart = restart_services,
            )
            self._packages[router] = '%s/%s.deb' %(base_path, mesh.routers[router].hostname.lower())
        
        logging.debug('Writing control files...')
        
        dump_config_files(base_path, self._files)
        
        #Begin packaging into dpkg
        logging.info('Assembling files for debs...')
        for plugin in configPlugins:
            logging.debug('Processing package files from plugin %s...' %(plugin))
            dump_config_files(base_path, plugin.files())
        
        for router in self._files:
            logging.info('Building package for router: %s' %(router))
            router_path = os.path.abspath(base_path + '/' + router)
            sCMD = 'fakeroot debian/rules binary'
            process = subprocess.Popen(sCMD, shell=True, stdout=subprocess.PIPE, cwd=router_path)
            process.wait()
            if process.returncode != 0:
                raise Exception('Package generation failed in %s.  Do you have debhelper and fakeroot installed?' %(base_path))

