#!/usr/bin/env python

import datetime, glob, os, shutil, subprocess, tempfile, logging, sys, argparse
import ipaddr, probstat, IPy, paramiko, yapsy
from interfaces import *

logging.basicConfig(level=logging.DEBUG)

from yapsy.PluginManager import PluginManager
from tunnelobjects import *

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
    #Find and load plugins
    pm = PluginManager(categories_filter={'Default': yapsy.IPlugin.IPlugin})
    pm.setPluginPlaces(["/usr/share/openmesher/plugins", "~/.openmesher/plugins", "./plugins"])
    pm.setPluginInfoExtension('plugin')
    pm.setCategoriesFilter({
        'config': IOpenMesherConfigPlugin,
        'package': IOpenMesherPackagePlugin,
        'deploy': IOpenMesherDeployPlugin,
   })
    pm.collectPlugins()
    
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, description="Generate configuration files for an OpenVPN mesh")
    parser.add_argument('-r', '--router', action='append', help='Adds a router that can be a client and server')
    parser.add_argument('-s', '--server', action='append', help='Adds a router that can only act as a server, not a client.')
    parser.add_argument('-c', '--client', action='append', help='Adds a router than can only act as a client.  For example, a router that is behind NAT and not accessible by a public IP')
    parser.add_argument('-p', '--ports', action='append', default=['7000-7999'])
    parser.add_argument('-n', '--network', action='append', default=['10.99.99.0/24'])
    
    for plugin in pm.getAllPlugins():
        pm.activatePluginByName(plugin.name)
        plugin.plugin_object.setupargs(parser)
    
    arg = parser.parse_args()
    
    # Call activate() on all plugins so they prep themselves for use
    for plugin in pm.getAllPlugins():
        plugin.plugin_object.activate()
    
    
    port_list = []
    try:
        for portrange in arg.ports:
            portstart, portstop = portrange.split('-')
            port_list += range(int(portstart),int(portstop))
    except ValueError as e:
        print 'Invalid port range: %s' %(portrange)
        raise e
    
    from linkmesh import create_link_mesh
    linkmesh = create_link_mesh(routers=arg.router, servers=arg.server, clients=arg.client)
    
    m = Mesh(linkmesh, port_list, arg.network)
    
    files = None
    
    # Run through config plugins
    for plugin in pm.getPluginsOfCategory('config'):
        plugin.plugin_object.process(m, arg)
        if files:
            files = nested_dict_merge(files, plugin.plugin_object.files())
        else:
            files = plugin.plugin_object.files()
    
    # Run through packaging plugins
    for plugin in pm.getPluginsOfCategory('package'):
        plugin.plugin_object.process(m, arg)
        if files:
            files = nested_dict_merge(files, plugin.plugin_object.files())
        else:
            files = plugin.plugin_object.files()


if __name__ == "__main__":
    main()
