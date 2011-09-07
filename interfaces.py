from yapsy.IPlugin import IPlugin

class IOpenMesherBasePlugin(IPlugin):
    def setupargs(self, parser):
        """
            Plugins can add their own cli switches by calling 'parser.add_argument'.
            parser: an argparse ArgumentParser object.
            Function does not return anything.
        """
        #example:
        #parser.add_argument('--myarg', action='store', help='Specify myarg')
        pass
    

class IOpenMesherConfigPlugin(IOpenMesherBasePlugin):
    """Interface for configuration plugins.  Accepts a mesh object, returns a dictionary of filenames and contents"""
    
    def process(self, mesh, **kwargs):
        """ Begin plugin processing """
        pass
    
    
    def files(self):
        """ Return a dictionary of routers containing a dictionary of filenames and contents """
        return {}
    
    def service_to_restart(self):
        """ Returns a string containing the name of a service to restart, such as 'openvpn'"""
        return ''


class IOpenMesherPackagePlugin(IOpenMesherBasePlugin):
    """
        Interface for packaging plugins.  Accepts a mesh object and some basic
        packaging parameters and then returns a dictionary of routers containing
        a dictionary of files and deployment actions for those files
    """
    
    def process(self, mesh, pkgauthor = 'aaron@heyaaron.com', pkgversion = '1.0', **kwargs):
        """
            Perform the actual work of creating package files and building the packages/
        """
        pass
    
    def files(self):
        """ Return a dictionary of routers containing a dictionary of filenames and contents """
        return {}
    
    def service_to_restart(self):
        """ Returns a string containing the name of a service to restart, such as 'openvpn'"""
        return ''
    
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
    
    def deploy(self, deploydict, stoponfailure=True):
        """
            Performs the actual deployment to a system.
        """
        pass
    
    def service_to_restart(self):
        """ Returns a string containing the name of a service to restart, such as 'openvpn'"""
        return ''

