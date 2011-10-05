import logging, interfaces, os
from datetime import datetime

class Shorewall(interfaces.IOpenMesherConfigPlugin):
    def activate(self):
        self._register('shorewall/interfaces.conf')
        self._register('shorewall/rules.conf')
    
    def setupargs(self, parser):
        parser.add_argument('--wanzone', action='store', default='wan', help='Name of the WAN zone in Shorewall')
        parser.add_argument('--fwzone', action='store', default='fw', help='Name of the Firewall zone in Shorewall')
        parser.add_argument('--vpnzone', action='store', default='vpn', help='Name of the VPN zone in Shorewall')
    
    def process(self, mesh, cliargs=None):
        logging.debug('Generating Shorewall config...')
        self._files = {}
        for router in mesh.links:
            self._files[router] = {}
            self._files[router]['/shorewall/interfaces.mesh'] = self._templates['shorewall/interfaces.conf'].render(links = mesh.links[router], vpnzone=cliargs.vpnzone, fwzone=cliargs.fwzone, wanzone=cliargs.wanzone)
            self._files[router]['/shorewall/rules.mesh'] = self._templates['shorewall/rules.conf'].render(links= mesh.links[router], vpnzone=cliargs.vpnzone, fwzone=cliargs.fwzone, wanzone=cliargs.wanzone)
            
        return True
    
    def files(self):
        """ Return a dictionary of routers containing a dictionary of filenames and contents """
        return self._files

