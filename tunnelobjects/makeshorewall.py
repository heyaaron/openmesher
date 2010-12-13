#!/usr/bin/env python
from StringIO import StringIO
from tunnelobjects import *

def makeshorewall(mesh):
    print 'Generating Shorewall config...'
    shorewallfiles = {}
    for router in mesh.links:
        shorewallfiles[router] = {}
        interfaces = StringIO()
        rules = StringIO()
        
        for link in mesh.links[router]:
            interfaces.write('vpn\t%s\n' %(link.iface))
            rules.write('ACCEPT\twan\tfw\ttcp\t%s\n' %(link.port))
            rules.write('ACCEPT\twan\tfw\tudp\t%s\n' %(link.port))
        shorewallfiles[router]['/shorewall/rules.mesh'] = rules.getvalue()
        shorewallfiles[router]['/shorewall/interfaces.mesh'] = interfaces.getvalue()
    return shorewallfiles

