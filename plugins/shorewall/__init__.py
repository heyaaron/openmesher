import logging, interfaces, os
from StringIO import StringIO
from datetime import datetime


class Shorewall(interfaces.IOpenMesherConfigPlugin):
    def activate(self):
        self._register('shorewall/interfaces.conf')
        self._register('shorewall/rules.conf')
    
    def process(self, mesh, cliargs=None):
        logging.debug('Generating Shorewall config...')
        self._files = {}
        for router in mesh.links:
            self._files[router] = {}
            interfaces = StringIO()
            rules = StringIO()
            
            self._files[router]['/shorewall/interfaces.mesh'] = self._templates['shorewall/interfaces.conf'].render(links = mesh.links[router], zone='vpn')
            self._files[router]['/shorewall/rules.mesh'] = self._templates['shorewall/rules.conf'].render(links= mesh.links[router])
            
        return True
    
    def files(self):
        """ Return a dictionary of routers containing a dictionary of filenames and contents """
        return self._files

