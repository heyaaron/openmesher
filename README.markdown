OpenMesher v0.5
===============
Copyright (c) 2010 Aaron C. de Bruyn <aaron@heyaaron.com>

OpenMesher is a better TunnelDigger.  They both basically create OpenVPN point to point tunnels, but OpenMesher has newer features and fixes.

First off, I would like to say thank you to the developers of TunnelDigger.  I hope they don't take the following list of improvements as a slam on a great tool that helped me for many years.

Here is a list of improvements:

* OpenMesher takes a simple list of routers and meshes them.  TunnelDigger requires you to explicitly specify each link between routers.
* OpenMesher takes a list of netblocks (10.1.2.0/24, 10.1.15.0/28, or whatever) and automatically allocates /30s from each block for assignment to P2P interfaces.  TunnelDigger requires you to manually specify IPs on *each* side of the p2p link.
* OpenMesher has support for plugins:  We currently support generating Quagga, reverse DNS, OpenVPN, Shorewall, and deb config files for deployment from a deb.
* Module -- Quagga: We can generate a ripd.conf and zebra.conf for each router
* Module -- ReverseDNS: We can generate a BIND reverse DNS file for each IP used in the p2p /30 blocks.
* Module -- OpenVPN: Obviously we generate the OpenVPN config files for the p2p links
* Module -- Shorewall: We generate files that can be included by your interfaces and rules file to allow the VPN p2p links to connect and route
* Module -- MakeDEBs: We generate deb files that include all the module files along with commands to restart services and package them up for deployment
* Module -- Deploy: Not quite ready yet--SCPs the DEB files up to the routers for easier deployment.
* Perl sucks
* TunnelDigger appears unmaintained
* TunnelDigger generates config files that aren't compatible with the latest version of OpenVPN
* TunnelDigger generates debs using an old format
* TunnelDigger uses PKI where I think shared keys work just fine--although adding CA support is fairly easy and is planned for a future release.


Dependencies
============
An easy way to install the dependencies is:
    pip install -r /path/to/openmesher/requirements.txt

If you don't have 'pip', try the following on a Debian-based system:
    sudo apt-get install python-pip


Example Configs
===============

One-off Quagga Configs
----------------------
When you run openmesher.py, it will look for a folder named after the router and import statements from specially named files.
For the moment, it's easiest to look at the source--but the following files are currently read for Quagga:

    zebra.main - Imported into the main config area of zebra
    ripd.main - Imported into the main config area of ripd
    ripd.interfaces - Added after all the auto-generated interfaces.  Can be used to add additional interfaces.
    ripd.router - Imported into the 'router rip' context
    ripd.acl - Imported after the auto-generated 'access-list' entries.

Example Run
-----------
(openmesher)08:06 /data/aaron/code/openmesher (hotfix/update-readme-for-v0.5)$ ./openmesher.py --router rtr1.cust.tld --server rtr2.cust.tld --client rtr3.cust.tld
    DEBUG:root:PluginManager skips /usr/share/openmesher/plugins (not a directory)
    DEBUG:root:PluginManager skips /data/aaron/code/openmesher/~/.openmesher/plugins (not a directory)
    DEBUG:root:PluginManager walks into directory: /data/aaron/code/openmesher/plugins
    DEBUG:root:PluginManager found a candidate: 
    	/data/aaron/code/openmesher/plugins/makedebs.yapsy-plugin
    DEBUG:root:PluginManager found a candidate: 
    	/data/aaron/code/openmesher/plugins/openvpn.yapsy-plugin
    DEBUG:root:PluginManager found a candidate: 
    	/data/aaron/code/openmesher/plugins/shorewall.yapsy-plugin
    DEBUG:root:PluginManager found a candidate: 
    	/data/aaron/code/openmesher/plugins/quagga.yapsy-plugin
    DEBUG:root:PluginManager found a candidate: 
    	/data/aaron/code/openmesher/plugins/reversedns.yapsy-plugin
    DEBUG:root:adding client rtr3.cust.tld to server rtr2.cust.tld
    DEBUG:root:adding router rtr1.cust.tld to server rtr2.cust.tld
    DEBUG:root:adding client rtr3.cust.tld to router rtr1.cust.tld
    Loaded 64 /30s
    DEBUG:root:Creating router object: rtr2.cust.tld
    DEBUG:root:Creating router (client): rtr3.cust.tld
    DEBUG:root:Creating router (client): rtr1.cust.tld
    DEBUG:root:Creating router object: rtr1.cust.tld
    DEBUG:root:Creating router (client): rtr3.cust.tld
    DEBUG:root:6 links needed
    DEBUG:root:61 subnets available
    DEBUG:root:996 ports available
    DEBUG:root:Activating plugin: Default.MakeDEBs
    DEBUG:root:Generating debs...
    DEBUG:root:Activating plugin: Default.OpenVPN
    DEBUG:root:Generating OpenVPN config...
    DEBUG:root:Activating plugin: Default.Shorewall
    DEBUG:root:Generating Shorewall config...
    DEBUG:root:Activating plugin: Default.Quagga
    DEBUG:root:Generating Quagga config...
    WARNING:root:You did not provide a password or enable password for quagga, using the default 'secret123' for router rtr3.cust.tld
    WARNING:root:You did not provide a password or enable password for zebra, using the default 'secret123' for router rtr3.cust.tld
    WARNING:root:You did not provide a password or enable password for quagga, using the default 'secret123' for router rtr2.cust.tld
    WARNING:root:You did not provide a password or enable password for zebra, using the default 'secret123' for router rtr2.cust.tld
    WARNING:root:You did not provide a password or enable password for quagga, using the default 'secret123' for router rtr1.cust.tld
    WARNING:root:You did not provide a password or enable password for zebra, using the default 'secret123' for router rtr1.cust.tld
    DEBUG:root:Activating plugin: Default.ReverseDNS
    DEBUG:root:Generating DNS config...
    Base path: /tmp/openmesher-XTrKQk
    Building package for router: rtr3.cust.tld
    Building package for router: rtr2.cust.tld
    Building package for router: rtr1.cust.tld
    (openmesher)08:07 /data/aaron/code/openmesher (hotfix/update-readme-for-v0.5)$ 


If you go look in the 'Base path' folder (in this case /tmp/openmesher-WvxXAI), you will find a .deb file for each router.
You can SCP those up to each router and use 'dpkg -i file.deb' to install them.
Please be careful though, these files by default contain OpenVPN .conf and .key files as well as Quagga ripd.conf and zebra.conf files.  Keep them safe.
If you already have an OpenVPN and/or Quagga conf, these files will be overwritten during the package install.
Also, OpenVPN, Quagga, and Shorewall will be restarted when installing the debs.


Developers and other geek-ilk
=============================
* Github rocks, fork it.
* Patches are welcome
* If you don't like the GitHub RSS feeds, you can follow @openmesher on twitter
* No mailing lists, IRC channels, etc...  Not a big-enough project at the moment.

