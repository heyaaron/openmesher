from yapsy.IPlugin import IPlugin

class IOpenMesherPlugin(IPlugin):
    def process(self, mesh, cliargs = None):
        """ Begin plugin processing """
        return False
    
    def files(self):
        """ Return a dictionary of routers containing a dictionary of filenames and contents """
        return {}


class IOpenMesherPluginTest(IPlugin):
    def process(self):
        """ Begin plugin processing """
        pass
    
    def files(self):
        """ Return a dictionary of routers containing a dictionary of filenames and contents """
        return {}
    
    def service_to_restart(self):
        """ Returns a string containing the name of a service to restart, such as 'openvpn'"""
        return ''
    
    #TODO: Need to output the folder containing files that makedebs needs to collect
