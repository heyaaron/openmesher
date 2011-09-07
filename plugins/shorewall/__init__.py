import logging, interfaces, os
from StringIO import StringIO
from datetime import datetime
from jinja2 import Environment, FileSystemLoader


class Shorewall(interfaces.IOpenMesherConfigPlugin):
    def __init__(self):
        env = Environment(loader=FileSystemLoader('/home/aaron/code/openmesher/plugins/shorewall'))
        
        self._files = {}
        self.interfaces_template = env.get_template('interfaces.conf')
        print self.interfaces_template
    
    def process(self, mesh, cliargs=None):
        logging.debug('Generating Shorewall config...')
        self._files = {}
        for router in mesh.links:
            self._files[router] = {}
            interfaces = StringIO()
            rules = StringIO()
            
            
            logging.debug(self.interfaces_template.render(links = mesh.links[router], zone='vpn'))
            
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

