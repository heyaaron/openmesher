#!/usr/bin/env python

import datetime, glob, os, shutil, subprocess, tempfile, logging, sys, argparse
import ipaddr, probstat, IPy, paramiko, yapsy
from interfaces import *
from lib import *

from yapsy.PluginManager import PluginManager
from tunnelobjects import *

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
    
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, description="Generate, package, and deploy an OpenVPN mesh")
    parser.add_argument('-r', '--router', action='append', help='Adds a router that can be a client and server')
    parser.add_argument('-s', '--server', action='append', help='Adds a router that can only act as a server, not a client.')
    parser.add_argument('-c', '--client', action='append', help='Adds a router than can only act as a client.  For example, a router that is behind NAT and not accessible by a public IP')
    parser.add_argument('-p', '--ports', action='append', default=['7000-7999'])
    parser.add_argument('-n', '--network', action='append', default=['10.99.99.0/24'])
    parser.add_argument('-v', '--verbose', action='append')
    
    for plugin in pm.getAllPlugins():
        pm.activatePluginByName(plugin.name)
        plugin.plugin_object.setupargs(parser)
    
    arg = parser.parse_args()
    
    router_count = arg.router or 0
    server_count = arg.server or 0
    client_count = arg.server or 0
    
    if router_count + server_count + client_count < 2:
        parser.print_help()
        raise ValueError('You must have a combination of two or more routers, servers, and clients')

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
    configPlugins = []
    for plugin in pm.getPluginsOfCategory('config'):
        plugin.plugin_object.process(m, arg)
        configPlugins.append(plugin.plugin_object)
        if files:
            files = nested_dict_merge(files, plugin.plugin_object.files())
        else:
            files = plugin.plugin_object.files()
    
    # Run through packaging plugins
    packagePlugins = []
    for plugin in pm.getPluginsOfCategory('package'):
        plugin.plugin_object.process(m, configPlugins=configPlugins, cliargs=arg)
        packagePlugins.append(plugin.plugin_object)
    
    # Run through deployment plugins
    for plugin in pm.getPluginsOfCategory('deploy'):
        plugin.plugin_object.deploy(packagePlugins=packagePlugins, cliargs=arg, stoponfailure=False)




if __name__ == "__main__":
    #TODO: Set debug level based on -vvv
    logging.basicConfig(level=logging.DEBUG)
    main()
