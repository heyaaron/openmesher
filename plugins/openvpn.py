import logging, interfaces
from StringIO import StringIO

class OpenVPN(interfaces.IOpenMesherPlugin):
    def __init__(self):
        self._openvpnfiles = {}
    
    def process(self, mesh):
        logging.debug('Generating OpenVPN config...')
        print "AAAGH!"
        self._openvpnfiles = {}
        for router in mesh.links:
            self._openvpnfiles[router] = {}
            
            for link in mesh.links[router]:
                linkconfig = StringIO()
                #BUG: Most of this should be imported from a config file
                linkconfig.write('port %s\n' %(link.port))
                linkconfig.write('proto udp\n')
                linkconfig.write('dev %s\n' %(link.iface))
                linkconfig.write('dev-type tun\n')
                linkconfig.write('keepalive 15 30\n')
                linkconfig.write('persist-tun\n')
                linkconfig.write('persist-key\n')
                linkconfig.write('passtos\n')
                linkconfig.write('comp-lzo\n')
                linkconfig.write('user nobody\n')
                linkconfig.write('group nogroup\n')
                linkconfig.write('verb 3\n')
                linkconfig.write('management 127.0.0.1 %s\n' %(link.port))
                linkconfig.write('secret %s\n' %(link.linkname() + '.key'))
                #BUG: Put this back in after testing
                #linkconfig.write('daemon %s\n'%(link.linkname()))
                
                if link.isServer(router):
                    linkconfig.write('local %s\n' %(link.server.fqdn.lower()))
                    linkconfig.write('ifconfig %s %s\n'%(link.block[1], link.block[2]))
                else:
                    linkconfig.write('remote %s\n' %(link.server.fqdn.lower()))
                    linkconfig.write('ifconfig %s %s\n' %(link.block[2], link.block[1]))
                
                self._openvpnfiles[router]['/openvpn/' + link.linkname() + '.conf'] = linkconfig.getvalue()
                self._openvpnfiles[router]['/openvpn/' + link.linkname() + '.key'] = link.key
    
    def files(self):
        """ Return a dictionary of routers containing a dictionary of filenames and contents """
        return self._openvpnfiles

