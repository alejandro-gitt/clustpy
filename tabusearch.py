import networkx as nx
import random
from mymod import mymodularity
from random import randrange

def max_of_nonimprovements(net_size):
    return net_size/2
def find_nodes_community(communities, target_node):
    '''
    This function takes a list of communities to find which one hosts the target node
    
    Parameters
    ----------
    communities : list or iterable of set of nodes
    groups of nodes, one of which, contains our targeted node

    target_node : int
    node to be found in one of the communities given
    
    Returns
    -------
    host_community_position : Position of the community that contains the node in the given list 'communities'
    '''

    if not any([target_node in comm for comm in communities]):
        raise NameError('Target node not found in any of the given communities')


    i = 0
    for community in communities:
                
        if any([target_node in community]):
            host_community_position = i
            return host_community_position

        i = i+1

def solution_from_move(s_iter, node):
    '''
     In this method, we want to move 'node', so we choose randomly one of the next options:
     - Move node from its current community to another existing one (randomly chosen).
     - Create a new community and insert the node in it.

     Buscamos en este metodo mover un solo nodo, escogiendo aleatoriamente entre las opciones:
     - Mover el nodo de su comunidad a otra 
     - Crear una nueva comunidad e incluir el nodo en esta.
     '''
   
    current_community_index = find_nodes_community(s_iter, node) 

    def create_new_community(communities,node):

        communities.append(frozenset({node}))
        communities_setted = [set(community) for community in communities]
        communities_setted[current_community_index].remove(node)
        final_sol = [frozenset(community_setted) for community_setted in communities_setted]

        for com in final_sol:
            if len(com) == 0:# It is an empty community
                final_sol.remove(com)
    
        return final_sol

    def change_to_random_community(communities, node):
        # Movemos el nodo de su comunidad actual a otra aleatoria
        # Moving node from current community to a random, different community

        dest_community_index = randrange(0,len(communities),1)
        while(dest_community_index == current_community_index):
            dest_community_index = randrange(0,len(communities),1)
        
        # Añadimos el nodo a destination_community y lo eliminamos el original:
        # Copiamos las comunidades en len(communities) 'sets' en lugar de frozensets para poder añadir y
        # eliminar, aunque luego lo volveremos a convertir en frozenset

        communities_setted = [set(community) for community in communities]
        communities_setted[dest_community_index].add(node)
        communities_setted[current_community_index].remove(node)
        new_random_partition = [frozenset(community_setted) for community_setted in communities_setted]
        #If a community turns out empty, we need to remove it
        for com in new_random_partition:
            if len(com) == 0:# It is an empty community
                new_random_partition.remove(com)

        return new_random_partition
    

    if len(s_iter) <= 1:
        result = create_new_community(s_iter,node)
    else:
        result = random.choice([change_to_random_community,create_new_community])(s_iter,node)
        
    return result

def explore_neighborhood(network, s_iter, s_best, tabu_moves, s_neigh, node_best):

    node_best = 0
    for node in network.nodes:
        s_move = solution_from_move(s_iter[:], node) 

        if mymodularity(network,s_move) > mymodularity(network,s_best):
            tabu_moves[node] = 0
        
        if tabu_moves[node] == 0 and (node_best == 0 or mymodularity(network,s_move) > mymodularity(network,s_neigh)):
            node_best = node
            s_neigh = s_move[:]
    
    return tabu_moves, s_neigh, node_best

def tabu_modularity_optimization(network, s_init, max_idle = 1):

    tabu_tenure = 100 # maximo numero de iteraciones en los que un mismo movimiento no se puede repetir
    tabu_moves = [] #contador de movimientos prohibidos, las posiciones son el entero que representa al nodo y el valor es el numero de movimientos restantes para poder volver a moverlo (siendo el maximo, tabu_tenure)
    max_idle = max_idle #max numero de iteraciones inactivas, posteriormente lo calculamos en funcion del tamaño del grafo
    num_idle = 0 #numero de iteraciones inactivas (AKA que no implican una mejora)
    s_iter = [] #solucion de la iteracion actual
    s_neigh = [] #solucion en el vecindario (neighbourhood)
    node_best = None #nodo con el mejor movimiento
   
    #Inicializamos
    tabu_moves = [0] * (max(network.nodes) + 1)
    num_idle = 0
    s_iter = s_init
    s_best = s_init
    vueltas = 0
    while num_idle < max_idle:
        vueltas = vueltas + 1
        (tabu_moves, s_neigh, node_best) = explore_neighborhood(network, s_iter[:], s_best[:], tabu_moves[:], s_neigh[:], node_best)
        for node in network.nodes:
            #reducimos los movimientos de tabu
            tabu_moves[node] = max(0,tabu_moves[node]-1) 
            
        tabu_moves[node_best] = tabu_tenure
        s_iter = s_neigh[:]
        if mymodularity(network, s_neigh[:]) > mymodularity(network, s_best[:]):
            s_best = s_neigh[:]
            num_idle = 0
        else:
            num_idle = num_idle + 1
    return s_best
    