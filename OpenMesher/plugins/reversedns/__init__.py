import logging, os, IPy
from StringIO import StringIO
from openmesher.interfaces import IOpenMesherConfigPlugin

class ReverseDNS(IOpenMesherConfigPlugin):
    def activate(self):
        self._register('reversedns/reverse.conf')
        
        self._reverse_template = self._env.get_template('reversedns/reverse.conf')
    
    def process(self, mesh, cliargs = None):
        logging.debug('Generating DNS config...')
        
        rdns = StringIO()
        for router in mesh.links:
            for link in mesh.links[router]:
                if link.isServer(router):
                    ip1 = IPy.IP(str(link.block[1]))
                    ip2 = IPy.IP(str(link.block[2]))
                    #BUG: Need to allow reversing to alternate domain names if p2p routing block is private
                    rdns.write(self._templates['reversedns/reverse.conf'].render(ip1=ip1, ip2=ip2, links=mesh.links[router]))
                self._files[router] = {'/mesh-reverse.db': rdns.getvalue()}

