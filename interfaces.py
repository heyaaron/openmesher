from yapsy.IPlugin import IPlugin

class IOpenMesherPlugin(IPlugin):
    def __init__(self):
        self.is_activated = True
        super(IPlugin, self).__init__()
    
    def process(self, mesh):
        """ Begin plugin processing """
        return False
    
    def files(self):
        """ Return a dictionary of routers containing a dictionary of filenames and contents """
        return {}


class IOpenMesherPluginTest(IPlugin):
    def __init__(self):
        self.is_active = True
    
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
