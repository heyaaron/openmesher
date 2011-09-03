import logging, interfaces, os, IPy
from StringIO import StringIO

class Shorewall(interfaces.IOpenMesherPlugin):
    def __init__(self):
        self._files = {}
    
    def process(self, mesh):
        logging.debug('Generating DNS config...')
        self._files = {}
        
        rdns = StringIO()
        for router in mesh.links:
            for link in mesh.links[router]:
                if link.isServer(router):
                    ip1 = IPy.IP(str(link.block[1]))
                    ip2 = IPy.IP(str(link.block[2]))
                    #BUG: fqdn might not be populated if just using hostnames.
                    #BUG: Need to allow reversing to alternate domain names if p2p routing block is private
                    #BUG: Need to put iface name in rev dns
                    rdns.write('%s\t\tPTR\t%s.\n' %(ip1.reverseName(), link.server.fqdn))
                    rdns.write('%s\t\tPTR\t%s.\n' %(ip2.reverseName(), link.client.fqdn))
        self._files['dnsserver'] = {'/etc/mesh-reverse.db': rdns.getvalue()}
        return True
    
    def files(self):
        """ Return a dictionary of routers containing a dictionary of filenames and contents """
        return self._files

