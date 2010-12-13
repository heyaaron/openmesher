#!/usr/bin/env python

#import ConfigParser, datetime, glob, ipaddr, os, paramiko, probstat, shutil, subprocess, tempfile, IPy
from StringIO import StringIO
from tunnelobjects import *

def makerevdns(mesh):
    print 'Generating Reverse DNS config...'
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
    return rdns.getvalue()

