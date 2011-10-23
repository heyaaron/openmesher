OpenMesher v0.6.3
=================
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

Please be careful with the generated deb files--they contain OpenVPN .key files as well as Quagga ripd.conf and zebra.conf files which have passwords in them.  Keep them safe.

If you specify the --sshdeploy switch, OpenMesher will attempt to copy the generated debs to the routers.
OpenMesher WILL NOT attempt to auto-install the packages or restart services.  You will need to do it by hand at the moment.  (I use cssh to connect to all the routers and then run 'dpkg -i `hostname`.deb').

When you install the package, the openvpn, shorewall, and quagga services will be restarted.  You can make your own custom postinst.conf file that does not restart the services.  Eventually there will be a flag to restart or not.

Developers and other geek-ilk
=============================
* Github rocks, fork it.
* Patches are welcome
* If you don't like the GitHub RSS feeds, you can follow @openmesher on twitter
* No mailing lists, IRC channels, etc...  Not a big-enough project at the moment.

