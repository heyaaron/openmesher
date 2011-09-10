#!/usr/bin/env python

import datetime, glob, os, shutil, subprocess, tempfile, logging, sys, argparse
import ipaddr, probstat, IPy, paramiko, yapsy

logging.basicConfig(level=logging.DEBUG)

from yapsy.PluginManager import PluginManager
from tunnelobjects import *
from tunnelobjects.makedebs import makedebs

from makepackage import package_generator

def dump_to_file(fname, data, clobber = False):
    if clobber and os.path.isfile(fname):
        os.unlink(fname)
    fh = open(fname, 'w')
    fh.write(data)
    fh.close()

def nested_dict_merge(d1,d2):
    merged = d1.copy()
    for k,v in d2.iteritems():
        if merged.has_key(k):
            if type(merged[k]) is dict:
                merged[k] = nested_dict_merge(merged[k], v)
            else:
                raise KeyError('Collision in key %s type %s' %(k, type(merged[k])))
        else:
            merged[k] = v
    return merged

def main():
    parser = argparse.ArgumentParser(description="Generate, package, and deploy an OpenVPN mesh")
    parser.add_argument('-r', '--router', action='append', help='Adds a router that can be a client and server')
    parser.add_argument('-s', '--server', action='append', help='Adds a router that can only act as a server, not a client.')
    parser.add_argument('-c', '--client', action='append', help='Adds a router than can only act as a client.  For example, a router that is behind NAT and not accessible by a public IP')
    parser.add_argument('-p', '--ports', action='append', default=['7000-7999'])
    parser.add_argument('-n', '--network', action='append', default=['10.99.99.0/24'])
    
    #BUG: This is hacky.  Plugins need to be able to be queried for their own list of args.
    parser.add_argument('--password', action='store', help='Specify quagga password')
    parser.add_argument('--enablepassword', action='store', help='Specify quagga enable password')
    
    arg = parser.parse_args()
    
    router_count = arg.router or 0
    server_count = arg.server or 0
    client_count = arg.server or 0
    
    if router_count + server_count + client_count < 2:
        parser.print_help()
        raise ValueError('You must have a combination of two or more routers, servers, and clients')
    
    port_list = []
    try:
        for portrange in arg.ports:
            portstart, portstop = portrange.split('-')
            port_list += range(int(portstart),int(portstop))
    except ValueError as e:
        print 'Invalid port range: %s' %(portrange)
        raise e
    
    #Find and load plugins
    pm = PluginManager(categories_filter={'Default': yapsy.IPlugin.IPlugin})
    pm.setPluginPlaces(["/usr/share/openmesher/plugins", "~/.openmesher/plugins", "./plugins"])
    pm.collectPlugins()
    
    from linkmesh import create_link_mesh
    linkmesh = create_link_mesh(routers=arg.router, servers=arg.server, clients=arg.client)
    
    m = Mesh(linkmesh, port_list, arg.network)
    
    files = None
    for plugin in pm.getAllPlugins():
        pm.activatePluginByName(plugin.name)
        p = plugin.plugin_object
        p.process(m, arg)
        if files:
            files = nested_dict_merge(files, p.files())
        else:
            files = p.files()
    
    package_generator(files)

if __name__ == "__main__":
    main()
