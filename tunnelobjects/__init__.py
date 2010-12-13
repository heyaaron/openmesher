import IPy, ipaddr, probstat, os, tempfile, subprocess

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
    
    def linkname(self):
        if self.server is None and self.client is None:
            raise Exception('Trying to retrieve link name of unnamed link')
        else:
            return '%s-%s' %(self.server.hostname, self.client.hostname)
    
    def _genkey(self):
        proc = subprocess.Popen("openvpn --genkey --secret /dev/stdout", shell=True, stdout=subprocess.PIPE)
        proc.wait()
        (stdout, stderr) = proc.communicate()
        if proc.returncode != 0:
            raise Exception('OpenVPN key gen failed for %s' %(self.linkname()))
        self.key = stdout
    
    def __init__(self, serverrouter, clientrouter, linkport, iface_number, block):
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
    
    def __init__(self, routers, ports, subnets):
        self.ports = ports
        for sub in subnets:
            blocks = ipaddr.IPNetwork(sub, strict=True).subnet(new_prefix=30)
            for block in blocks:
                self.subnets.append(block)
                
        print 'Loaded %s /30s' %(len(self.subnets))
        self.subnets.reverse()
        
        for rtr in routers:
            self.routers[rtr] = Router(rtr)
        
        for combo in probstat.Combination(self.routers.keys(), 2):
            newlink = Link(self.routers[combo[0]], self.routers[combo[1]], ports.pop(), self.iface_count, self.subnets.pop())
            try:
                if newlink not in self.links[combo[0]]:
                    self.links[combo[0]].append(newlink)
            except KeyError:
                self.links[combo[0]] = [newlink]
            
            try:
                if newlink not in self.links[combo[1]]:
                    self.links[combo[1]].append(newlink)
            except KeyError:
                self.links[combo[1]] = [newlink]
            
            self.iface_count += 1
        
        links_needed = 2^len(self.routers)
        subnets_available = len(self.subnets)
        ports_available = len(self.ports)
        
        if links_needed > subnets_available:
            raise Exception('Not enough subnets available: %s needed, %s available' %(links_needed, subnets_available))
        
        if links_needed > ports_available:
            raise Exception('Not enough ports available: %s needed, %s available' %(links_needed, ports_available))
    
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

