import IPy, ipaddr, probstat, os, tempfile, subprocess, logging

class Router():
    fqdn = ''
    hostname = ''
    domain = ''
    interfaces = []

    def __init__(self, name):
        if '.' in name:
            self.hostname = name.split('.')[0]
            self.domain = '.'.join(name.split('.')[1:])
            self.fqdn = name
        else:
            self.hostname = name
    
    def __unicode__(self):
        return '%s' %(self.fqdn or self.hostname)
    
    def __str__(self):
        return '%s' %(self.fqdn or self.hostname)


class Link():
    server = None
    client = None
    port = 0
    iface = None
    block = None
    key = None
    OpenVPNPath = None
    
    def linkname(self):
        if self.server is None and self.client is None:
            raise Exception('Trying to retrieve link name of unnamed link')
        else:
            return '%s-%s' %(self.server.hostname, self.client.hostname)
    
    def _genkey(self):
        proc = subprocess.Popen("%s --genkey --secret /dev/stdout" %(self.OpenVPNPath), shell=True, stdout=subprocess.PIPE)
        proc.wait()
        (stdout, stderr) = proc.communicate()
        if proc.returncode != 0:
            raise Exception('OpenVPN key gen failed for %s' %(self.linkname()))
        self.key = stdout
    
    def __init__(self, serverrouter, clientrouter, linkport, iface_number, block):
        #BUG: Hack because Ubuntu 11.10 moved openvpn from /bin to /sbin and the user doesn't have a path to /sbin.  Need to search path, then check /sbin
        for ovp in ['/bin', '/sbin', '/usr/bin', '/usr/sbin']:
            if os.path.isfile('%s/openvpn' %ovp):
                self.OpenVPNPath = "%s/openvpn" %(ovp)
                break
        
        if not self.OpenVPNPath:
            raise IOError('Unable to locate OpenVPN executable')
        
        self.block = block
        self.server = serverrouter
        self.client = clientrouter
        self.port = linkport
        self.iface = 'tun%s' %(iface_number)
        self.server.interfaces.append('tun%s' %(iface_number))
        self.client.interfaces.append('tun%s' %(iface_number))
        if self.key is None:
            self._genkey()
    
    def __unicode__(self):
        return 'Server: %s, Client: %s, Port: %s, Iface: %s Block: %s' %(self.server.fqdn, self.client.fqdn, self.port, self.iface, self.block)
    
    def __str__(self):
        return 'Server: %s, Client: %s, Port: %s, Iface: %s Block: %s' %(self.server.fqdn, self.client.fqdn, self.port, self.iface, self.block)

    def isServer(self, routerfqdn):
        return routerfqdn == self.server.fqdn


class Mesh():
    links = {}
    routers = {}
    iface_count = 0
    ports = []
    subnets = []
    
    def __init__(self, routerlinks, ports, subnets):
        logging.debug('Subnets available: %s' %(subnets))
        for sub in subnets:
            logging.debug('Processing subnet: %s' %(sub))
            blocks = ipaddr.IPNetwork(sub, strict=True).subnet(new_prefix=30)
            for block in blocks:
                logging.debug('P2P block available: %s' %(block))
                self.subnets.append(block)
                
        logging.debug('Loaded %s /30s' %(len(self.subnets)))
        self.subnets.reverse()
        
        links_needed = None
        #Create router objects for each router and client
        for rtr in routerlinks:
            logging.debug('Creating router object: %s' %(rtr))
            self.routers[rtr] = Router(rtr)
            for rtrcli in routerlinks[rtr]:
                logging.debug('Creating router (client): %s' %(rtrcli))
                self.routers[rtrcli] = Router(rtrcli)
        
        #For each router, create a link object, assign a server and client router object, assign ports and interface numbers along with a subnet.
        for rtr in routerlinks:
            for rtrclient in routerlinks[rtr]:
                logging.debug('Creating new link from %s to %s with iface %s' %(rtr, rtrclient, self.iface_count))
                try:
                    newlink = Link(self.routers[rtr], self.routers[rtrclient], ports.pop(), self.iface_count, self.subnets.pop())
                except IndexError as e:
                    raise IndexError('Not enough ports available.  Add additional port ranges and try again.')
                
                if not self.links.has_key(rtr):
                    self.links[rtr] = []
                self.links[rtr].append(newlink)
                
                if not self.links.has_key(rtrclient):
                    self.links[rtrclient] = []
                self.links[rtrclient].append(newlink)
                self.iface_count += 1
        
        #BUG: Wow--this is screwed up.  Bad math, requires too many ports, etc...
        links_needed = 0
        for srv in self.links:
            links_needed += len(self.links[srv])
        logging.debug('%s links needed' %(links_needed))
        
        subnets_available = len(self.subnets)
        logging.debug('%s subnets available' %(subnets_available))
        
        if links_needed > subnets_available:
            raise Exception('Not enough subnets available: %s needed, %s available' %(links_needed, subnets_available))
    
    def __unicode__(self):
        return '%s routers, %s links' %(len(self.routers), len(probstat.Combination(self.routers.keys(), 2)))
    
    def __str__(self):
        return '%s routers, %s links' %(len(self.routers), len(probstat.Combination(self.routers.keys(), 2)))
    
    def get_server_links(self, sRouter):
        rLinks = []
        for link in self.links[sRouter]:
            if link.server.name == sRouter:
                rLinks.append(link)
        return rLinks
    
    def get_client_links(self, sRouter):
        rLinks = []
        for link in self.links[sRouter]:
            if link.client.name == sRouter:
                rLinks.append(link)
        return rLinks

