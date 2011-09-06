OpenMesher v0.5
===============
Copyright (c) 2010 Aaron C. de Bruyn <aaron@heyaaron.com>

OpenMesher is a better TunnelDigger.  They both basically create OpenVPN point to point tunnels, but OpenMesher has newer features and fixes.

First off, I would like to say thank you to the developers of TunnelDigger.  I hope they don't take the following list of improvements as a slam on a great tool that helped me for many years.

Here is a list of improvements:

* OpenMesher takes a simple list of routers and meshes them.  TunnelDigger requires you to explicitally specify each link between routers.
* OpenMesher takes a list of netblocks (10.1.2.0/24, 10.1.15.0/28, or whatever) and automatically allocates /30s from each block for assignment to P2P interfaces.  TunnelDigger requires you to manually specify IPs on *each* side of the p2p link.
* OpenMesher has support for plugins:  We currently support generating quagga, reverse DNS, OpenVPN, Shorewall, and deb config files for deployment from a deb.
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


Example Config
==============

network-list
------------
A list of networks in CIDR format that can be used as IPs for p2p links.  Networks are chopped up into /30s automatically.
    10.99.0.0/16
    10.50.1.0/24


router-list
-----------
A list of routers.
    main-office.router.cust.tld
    southern-office.router.cust.tld
    backup-office.router.cust.tld
    vancouver-office.router.cust.tld


port-list
---------
A list of port ranges to be used for the OpenVPN connections
    7000-7999
    1500-1701


One-off Quagga Configs
----------------------
When you run openmesher.py, it will look for a folder named after the router and import statements from specially named files.
For the moment, it's easiest to look at the source--but the following files are currently read for quagga:

    zebra.main - Imported into the main config area of zebra
    ripd.main - Imported into the main config area of ripd
    ripd.interfaces - Added after all the auto-generated interfaces.  Can be used to add additional interfaces.
    ripd.router - Imported into the 'router rip' context
    ripd.acl - Imported after the auto-generated 'access-list' entries.


Output
------
Typical output looks something like this:
    aaron@tycho:~/code/openmesher$ ./openmesher.py 
    Loaded 64 /30s
    Generating Reverse DNS config...
    Generating Quagga config...
    Importing ./main-office.router.cust.tld/ripd.router
    Generating OpenVPN config...
    Generating Shorewall config...
    Generating deb configs...
    Base path: /tmp/openmesher-WvxXAI
    Building package for router: main-office.router.cust.tld
    Building package for router: southern-office.router.cust.tld
    Building package for router: backup-office.router.cust.tld
    Building package for router: vancouver-office.router.cust.tld
    aaron@tycho:~/code/openmesher$ 

If you go look in the 'Base path' folder (in this case /tmp/openmesher-WvxXAI), you will find a .deb file for each router.
You can scp those up to each router and use 'dpkg -i file.deb' to install them.
Please be careful though, these files by default contain OpenVPN .conf and .key files as well as Quagga ripd.conf and zebra.conf files.
If you already have an OpenVPN and/or Quagga conf, these files will be overwritten during the package install.

