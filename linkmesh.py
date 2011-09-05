import logging

def create_link_mesh(routers = None, servers = None, clients = None):
    conns = {}
    
    # Every server connects to all clients and all routers
    if servers:
        for server in servers:
            if not server in conns:
                conns[server] = []
            
            if clients:
                for client in clients:
                    if not client in conns[server]:
                        logging.debug('adding client %s to server %s' %(client, server))
                        conns[server].append(client)
            
            if routers:
                for router in routers:
                    if not router in conns[server]:
                        logging.debug('adding router %s to server %s' %(router, server))
                        conns[server].append(router)
    
    #Every router connects to all other routers and clients except itself
    if routers:
        for router in routers:
            if not router in conns:
                conns[router] = []
            
            for clientrouter in routers:
                if router == clientrouter:
                    continue
                
                if not clientrouter in conns[router]:
                    if conns.has_key(clientrouter):
                        if router in conns[clientrouter]:
                            logging.debug('reverse connection from clientrouter %s to router %s already exists' %(clientrouter, router))
                            continue
                        
                        logging.debug('adding clientrouter %s to router %s' %(clientrouter, router))
                        conns[router].append(clientrouter)
            
            
            if clients:
                for client in clients:
                    if client == router:
                        continue
                    
                    if not client in conns[router]:
                        logging.debug('adding client %s to router %s' %(client, router))
                        conns[router].append(client)
    
    #TODO: Need to also return a list of disconnected entities
    return conns
