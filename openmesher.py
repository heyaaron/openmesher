#!/usr/bin/env python

import datetime, glob, os, shutil, subprocess, tempfile, logging
import ipaddr, probstat, IPy, paramiko, yapsy

#RELEASE: Remove debug logging
logging.basicConfig(level=logging.DEBUG)

from yapsy.PluginManager import PluginManager
from tunnelobjects import *
from tunnelobjects.makerevdns import makerevdns
from tunnelobjects.makedebs import makedebs

from makepackage import package_generator

def slurpfile(fname, required = True):
    content = []
    try:
        fh = open(fname)
    except IOError as e:
        print 'Unable to open file: %s' %(fname)
        if required:
            raise e
        else:
            return False
    rawcontent = fh.readlines()
    fh.close()
    
    for line in rawcontent:
        content.append(line.strip())
    return content

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
    router_list = slurpfile('router-list')
    port_ranges = slurpfile('port-list')
    subnet_list = slurpfile('network-list', False)
    if not subnet_list:
        print 'No network-list file, using default subnet 10.99.99.0./24'
        subnet_list = '10.99.99.0/24'

    port_list = []
    for portrange in port_ranges:
        portstart, portstop = portrange.split('-')
        port_list += range(int(portstart),int(portstop))


    pm = PluginManager(categories_filter={'Default': yapsy.IPlugin.IPlugin})
    pm.setPluginPlaces(["/usr/share/openmesher/plugins", "~/.openmesher/plugins", "./plugins"])
    pm.collectPlugins()
    
    m = Mesh(router_list, port_list, subnet_list)
    
    rd = makerevdns(m)
    dump_to_file('rev.db', rd, True)

    files = None
    for plugin in pm.getAllPlugins():
        pm.activatePluginByName(plugin.name)
        p = plugin.plugin_object
        p.process(m)
        if files:
            files = nested_dict_merge(files, p.files())
        else:
            files = p.files()
    
    md = makedebs(m, ['openvpn', 'quagga', 'shorewall'], ['openvpn', 'quagga', 'shorewall'])
    files = nested_dict_merge(files, md)
    package_generator(files)


if __name__ == "__main__":
    main()
