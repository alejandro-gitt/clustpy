def modularity(G, communities, weight="weight", resolution=1):
    r"""Returns the modularity of the given partition of the graph.
    
    Parameters
    ----------
    G : NetworkX Graph

    communities : list or iterable of set of nodes
        These node sets must represent a partition of G's nodes.

    weight : string or None, optional (default="weight")
            The edge attribute that holds the numerical value used
            as a weight. If None or an edge does not have that attribute,
            then that edge has weight 1.

    resolution : float (default=1)
        If resolution is less than 1, modularity favors larger communities.
        Greater than 1 favors smaller communities.

    Returns
    -------
    Q : float
        The modularity of the paritition.

    Raises
    ------
    NotAPartition
        If `communities` is not a partition of the nodes of `G`.
        
    """
    if not isinstance(communities, list):
        communities = list(communities)
    if not is_partition(G, communities):
        raise NotAPartition(G, communities)
        
        directed = G.is_directed()
    if not nx.is_negatively_weighted(G): #Original code from networkx for positive weighted, directed and undirected edges.
        
        if directed:
            out_degree = dict(G.out_degree(weight=weight))
            in_degree = dict(G.in_degree(weight=weight))
            m = sum(out_degree.values())
            norm = 1 / m ** 2
        else:
            out_degree = in_degree = dict(G.degree(weight=weight))
            deg_sum = sum(out_degree.values())
            m = deg_sum / 2
            norm = 1 / deg_sum ** 2

        def community_contribution(community):
            comm = set(community)
            L_c = sum(wt for u, v, wt in G.edges(comm, data=weight, default=1) if v in comm)

            out_degree_sum = sum(out_degree[u] for u in comm)
            in_degree_sum = sum(in_degree[u] for u in comm) if directed else out_degree_sum

            return L_c / m - resolution * out_degree_sum * in_degree_sum * norm

        return sum(map(community_contribution, communities))
    
    else:
        # Our special case: negatively weighted edges
        if directed:
            pos_total_weight = sum(wt for u, v, wt in G.edges(data = weight, default=1) if wt > 0) #Sum all positive links
            neg_total_weight = sum(wt for u, v, wt in G.edges(data=weight, default=1) if wt < 0) #Sum all negative links
            
            out_degree  = dict(G.out_degree(weight=weight))
            in_degree = dict(G.in_degree(weight=weight))
            
            def community_contribution_directed_negatively_weighted(community):#Añadiendo extension de direccionadas
                comm = set(community)
                L_a = sum(wt for u, v, wt in G.edges(comm, data=weight, default=1) if v in comm) #L_c identical, sum of all weights within a community
                
                pos_degree_sum_out = sum([out_degree[u] for u in community])
                pos_degree_sum_in = 
                
                neg_degree_sum_out = 
                neg_degree_sum_in = 
                
                return L_a - (pos_degree_sum_out*pos_degree_sum_in)/(2*pos_total_weight) + (neg_degree_sum_out*neg_degree_sum_in)/(2*neg_total_weight)
            
            return (1/(2*(pos_total_weight + neg_total_weight)))*sum(map(community_contribution_directed_negatively_weighted, communities))
'''
En esto anterior, está añadida la extensión propia de redes direccionadas
'''
            
        else: #Negatively weighted, non directed 
            pos_total_weight = sum(wt for u, v, wt in G.edges(data = weight, default=1) if wt > 0) #Sum all positive links
            neg_total_weight = sum(wt for u, v, wt in G.edges(data=weight, default=1) if wt < 0) #Sum all negative links
            
            
            def community_contribution_negatively_weighted(community):
                comm = set(community)
                L_a = sum(wt for u, v, wt in G.edges(comm, data=weight, default=1) if v in comm) #L_c identical, sum of all weights within a community
                pos_degree_sum = sum(wt for u, v, wt in G.edges(comm, data=weight, default=1) if (v in comm and wt > 0))
                neg_degree_sum = sum(-wt for u, v, wt in G.edges(comm, data=weight, default=1) if (v in comm and wt < 0))# -wt porque tomamos los pesos con signo positivo
                
                return L_a - pos_degree_sum**2/(2*pos_total_weight) + neg_degree_sum**2/(2*neg_total_weight)
            
            return (1/(2*(pos_total_weight + neg_total_weight)))*sum(map(community_contribution_negatively_weighted, communities))
