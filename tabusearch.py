import networkx as nx
from mymod import mymodularity
import random

def max_of_nonimprovements(net_size):
    return net_size/2
def find_nodes_community(communities, target_node):
    ''' This function takes a list of communities to find which one hosts the target node
    
    Parameters
    ----------
    communities : list or iterable of set of nodes.
        groups of nodes, one of which, contains our targeted node

    target_node : int
     node to be found in one of the communities given
    
    Returns
    -------
    host_community_position : position of the community that contains the node in the given list 'communities'
    '''

    if not any([target_node in comm for comm in communities]):
        print('TARGET NODE NOT FOUND IN ANY OF THE COMMUNITIES')
        return -1

    i = 0
    for community in communities:
                
        if any([target_node in community]):
            host_community_position = i
            return host_community_position

        i = i+1

def solution_from_move(network, s_iter, node):
    #'move operator acts on one node aata time, moving it from its current community to another selected at random, or creating a new one.
    #Among the solutions in the neighbourhood, the best one is chosen to become the new current solution for the next iteration of the algorithm'
    
    #Por tanto buscamos en este metodo mover un solo nodo, escogiendo aleatoriamente entre las opciones:
    # - Mover el nodo de una comunidad a otra (aleatoria)
    # - Crear una nueva comunidad e incluir el nodo en esta.(El nodo solo puede estar en una comunidad a la vez)
    
    
    def change_to_random_community(network, s_iter, node):
        # En primer lugar, encontramos en que comunidad está node
        nodes_host_community = find_nodes_community()
        return new_random_partition
    
    return 

def explore_neighborhood(network, s_iter, s_best, tabu_moves, s_neigh, node_best):
    
    node_best = 0
    for node in network.nodes:
        s_move = solution_from_move(network, s_iter, node)
        if mymodularity(s_move) > mymodularity(s_best):
            tabu_moves[node] = 0
        
        if tabu_moves[node] == 0 and (node_best == 0 or mymodularity(s_move) > mymodularity(s_neigh)):
            node_best = node
            s_neigh = s_move
            
    return tabu_moves, s_neigh, node_best

def tabu_modularity_optimization(network, s_init):
    '''
    Initial_solution = group of nodes (partition of the network). I understand it as different sets of nodes which makes different communities
    '''
    tabu_tenure = 5 # maximo numero de iteraciones en los que un mismo movimiento no se puede repetir
    tabu_moves = [] #contador de movimientos prohibidos
    max_idle = 0 #max numero de iteraciones inactivas, posteriormente lo calculamos en funcion del tamaño del grafo
    num_idle = 0 #numero de iteraciones inactivas (AKA que no implican una mejora)
    s_iter = [] #solucion de la iteracion actual
    s_neigh = [] #solucion en el vecindario (neighbourhood)
    node_best = 0 #nodo con el mejor movimiento
    
    for node in network.nodes:
        #initialize the tabu moves 
        tabu_moves[node] = 0
        
    max_idle = max_of_nonimprovements(len(network.nodes))
    num_idle = 0
    s_iter = s_init
    s_best = s_init
    
    while num_idle < max_idle:
        (tabu_moves, s_neigh, node_best) =explore_neighborhood(network, s_iter, s_best, tabu_moves, s_neigh, node_best)
        for node in network.nodes:
            #decrease the tabu moves 
            tabu_moves[node] = max(0,tabu_moves[node]-1) 
            
        tabu_moves[node_best] = tabu_tenure
        s_iter = s_neigh
        if mymodularity(s_neigh) > mymodularity(s_best):
            s_best = s_neigh
            num_idle = 0
        else:
            num_idle = num_idle + 1
            
    return s_best
    