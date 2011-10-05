import logging
from jinja2 import Environment, FileSystemLoader, ChoiceLoader
from openmesher.interfaces import IOpenMesherConfigPlugin

class OpenVPN(IOpenMesherConfigPlugin):
    def activate(self):
        self._register('openvpn/openvpn.conf')
    
    def process(self, mesh, cliargs = None):
        logging.debug('Generating OpenVPN config...')
        self._files = {}
        for router in mesh.links:
            self._files[router] = {}
            
            for link in mesh.links[router]:
                self._files[router]['/openvpn/%s.conf' %(link.linkname())] = self._templates['openvpn/openvpn.conf'].render(link=link, isserver=link.isServer(router))
                self._files[router]['/openvpn/%s.key' %(link.linkname())] = link.key
    
    def files(self):
        """ Return a dictionary of routers containing a dictionary of filenames and contents """
        return self._files

