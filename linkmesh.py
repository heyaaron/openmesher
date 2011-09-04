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
                        conns[server].append(client)
            
            if routers:
                for router in routers:
                    if not router in conns[server]:
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
                    conns[router].append(clientrouter)
            
            if clients:
                for client in clients:
                    if client == router:
                        continue
                    
                    if not client in conns[router]:
                        conns[router].append(client)
    
    #TODO: Need to also return a list of disconnected entities
    return conns
