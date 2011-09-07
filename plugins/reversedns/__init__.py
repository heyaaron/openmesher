import logging, interfaces, os, IPy
from StringIO import StringIO

class ReverseDNS(interfaces.IOpenMesherConfigPlugin):
    def activate(self):
        self._reverse_template = self._env.get_template('reversedns/reverse.conf')
    
    def process(self, mesh, cliargs = None):
        logging.debug('Generating DNS config...')
        
        rdns = StringIO()
        for router in mesh.links:
            for link in mesh.links[router]:
                if link.isServer(router):
                    ip1 = IPy.IP(str(link.block[1]))
                    ip2 = IPy.IP(str(link.block[2]))
                    #BUG: fqdn might not be populated if just using hostnames.
                    #BUG: Need to allow reversing to alternate domain names if p2p routing block is private
                    #BUG: Need to put iface name in rev dns
                    rdns.write(self._reverse_template.render(ip1=ip1, ip2=ip2, links=mesh.links[router]))
                self._files[router] = {'/mesh-reverse.db': rdns.getvalue()}

