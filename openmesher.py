#!/usr/bin/env python

import datetime, glob, os, shutil, subprocess, tempfile, logging
import ipaddr, probstat, IPy, paramiko

#RELEASE: Remove debug logging
logging.basicConfig(level=logging.DEBUG)

from yapsy.PluginManager import PluginManager
from tunnelobjects import *
from tunnelobjects.makerevdns import makerevdns
from tunnelobjects.makequagga import makequagga
from tunnelobjects.makeopenvpn import makeopenvpn
from tunnelobjects.makeshorewall import makeshorewall
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


    simplePluginManager = PluginManager()
    simplePluginManager.setPluginPlaces(["/usr/share/openmesher/plugins", "~/.openmesher/plugins", "./plugins"])

    simplePluginManager.locatePlugins()
    simplePluginManager.loadPlugins()

    for plugin in simplePluginManager.getAllPlugins():
        print 'Loaded plugin: %s' %(plugin.name)

    m = Mesh(router_list, port_list, subnet_list)

    rd = makerevdns(m)
    dump_to_file('rev.db', rd, True)

    files = {}
    for plugin in simplePluginManager.getAllPlugins():
        print plugin
        print dir(plugin)
        print plugin.plugin_object
        p = plugin.plugin_object
        print p
        print dir(p)
        p.activate()
        p.process(m)
        files = nested_dict_merge(files,p.files())
    
    qc = makequagga(m)
#    ov = makeopenvpn(m)
    sw = makeshorewall(m)
    md = makedebs(m, ['openvpn', 'quagga', 'shorewall'], ['openvpn', 'quagga', 'shorewall'])
    
    files = nested_dict_merge(files, qc)
    files = nested_dict_merge(files, sw)
    files = nested_dict_merge(files, md)
    package_generator(files)



if __name__ == "__main__":
    main()
