import logging, interfaces, os
from StringIO import StringIO
from datetime import datetime

class Shorewall(interfaces.IOpenMesherPlugin):
    def __init__(self):
        self._files = {}
    
    def process(self, mesh, cliargs=None):
        logging.debug('Generating Shorewall config...')
        self._files = {}
        for router in mesh.links:
            self._files[router] = {}
            interfaces = StringIO()
            rules = StringIO()
            
            for link in mesh.links[router]:
                interfaces.write('vpn\t%s\n' %(link.iface))
                rules.write('ACCEPT\twan\tfw\ttcp\t%s\n' %(link.port))
                rules.write('ACCEPT\twan\tfw\tudp\t%s\n' %(link.port))
            self._files[router]['/shorewall/rules.mesh'] = rules.getvalue()
            self._files[router]['/shorewall/interfaces.mesh'] = interfaces.getvalue()
        return True
    
    def files(self):
        """ Return a dictionary of routers containing a dictionary of filenames and contents """
        return self._files

