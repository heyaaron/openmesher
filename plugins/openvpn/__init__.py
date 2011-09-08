import logging, interfaces
from StringIO import StringIO
from jinja2 import Environment, FileSystemLoader, ChoiceLoader

class OpenVPN(interfaces.IOpenMesherConfigPlugin):
    def activate(self):
        self._openvpn_template = self._env.get_template('openvpn/openvpn.conf')
    
    def process(self, mesh, cliargs = None):
        logging.debug('Generating OpenVPN config...')
        self._files = {}
        for router in mesh.links:
            self._files[router] = {}
            
            for link in mesh.links[router]:
                self._files[router]['/openvpn/%s.conf' %(link.linkname())] = self._openvpn_template.render(link=link)
                self._files[router]['/openvpn/%s.key' %(link.linkname())] = link.key
    
    def files(self):
        """ Return a dictionary of routers containing a dictionary of filenames and contents """
        return self._files

