import os, logging
from yapsy.IPlugin import IPlugin
from jinja2 import Environment, FileSystemLoader, ChoiceLoader, PackageLoader


class IOpenMesherBasePlugin(IPlugin):
    _enabled = False
    def setupargs(self, parser):
        """
            Plugins can add their own cli switches by calling 'parser.add_argument'.
            parser: an argparse ArgumentParser object.
            Function does not return anything.
            
            Unless overridden, the function will automatically create a cli arg for --classname to allow users to enable usage of the plugin.
        """
        parser.add_argument('--%s' %(self.__class__.__name__.lower()), action='store_true', help='Enable %s plugin' %(self.__class__.__name__.lower()))


class IOpenMesherConfigPlugin(IOpenMesherBasePlugin):
    """Interface for configuration plugins.  Accepts a mesh object, returns a dictionary of filenames and contents"""
    
    def __init__(self):
        self._files = {}
        self._templates = {}
        self._env = Environment(loader=ChoiceLoader([
                FileSystemLoader('%s/.openmesher/' %(os.path.expanduser('~'))),
                FileSystemLoader('%s/OpenMesher/plugins/' %(os.getcwd())),
                PackageLoader('OpenMesher', 'plugins'),
            ]))
    
    def _register(self, templatename):
        """ Register a template and prepare it for use """
        self._templates[templatename] = self._env.get_template(templatename)
    
    def process(self, mesh, **kwargs):
        """ Begin plugin processing """
        pass
    
    def files(self):
        """ Return a dictionary of routers containing a dictionary of filenames and contents """
        return self._files
    
    def service_to_restart(self):
        """ Returns a string containing the name of a service to restart, such as 'openvpn'"""
        return ''


class IOpenMesherPackagePlugin(IOpenMesherBasePlugin):
    """
        Interface for packaging plugins.  Accepts a mesh object and some basic
        packaging parameters and then returns a dictionary of routers containing
        a dictionary of files and deployment actions for those files
    """
    def __init__(self):
        self._files = {}
        self._packages = {}
        self._templates = {}
        self._env = Environment(loader=ChoiceLoader([
                FileSystemLoader('~/.openmesher/'),
                FileSystemLoader('%s/OpenMesher/plugins/' %(os.getcwd())),
                PackageLoader('OpenMesher', 'plugins'),
            ]))
    
    def _register(self, templatename):
        """ Register a template and prepare it for use """
        self._templates[templatename] = self._env.get_template(templatename)
    
    def process(self, mesh, pkgauthor = 'aaron@heyaaron.com', pkgversion = '1.0', **kwargs):
        """
            Perform the actual work of creating package files and building the packages/
        """
        pass
    
    def packages(self):
        """ Return a dictionary of routers containing an array of filenames to deploy """
        return self._packages
    
    def service_to_restart(self):
        """ Returns a string containing the name of a service to restart, such as 'openvpn'"""
        return None
    
    #TODO: Need to output the folder containing files that makedebs needs to collect


class IOpenMesherDeployPlugin(IOpenMesherBasePlugin):
    """
        Interface for deployment plugins.  Accepts a mesh object and some basic
        deployment parameters and then performs the deployment, returning a dictionary
        of routers and any appropriate info--such as stdout/stderr or just OK/Fail, etc...
    """
    
    def canrestart(self):
        """
            Is the plugin able to restart services?
        """
    
    def canreboot(self):
        """
            Is the plugin able to reboot the server?
        """
    
    def deploy(self, deploy_dict, cliargs, stoponfailure=False):
        """
            Performs the actual deployment to a system.
        """
        pass

