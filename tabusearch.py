import networkx as nx
import random
from mymod import mymodularity
from random import randrange
import math

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
    
    # Buscamos en este metodo mover un solo nodo, escogiendo aleatoriamente entre las opciones:
    # - Mover el nodo de una comunidad a otra (aleatoria)
    # - Crear una nueva comunidad e incluir el nodo en esta.(El nodo solo puede estar en una comunidad a la vez)
    current_community_index = find_nodes_community(s_iter, node) #INDICE DE LA COMUNIDAD EN LA QUE SE ENCUENTRA EL NODO ACTUALMENTE

    def create_new_community(communities,node):

        # Primero, creamos una nueva comunidad y añadimos nuestro nodo en ella
        communities.append(frozenset({node}))
        # Eliminamos el nodo de su comunidad origen
        communities_setted = [set(community) for community in communities]
        communities_setted[current_community_index].remove(node)
        final_sol = [frozenset(community_setted) for community_setted in communities_setted]

        for com in final_sol:
            if len(com) == 0:# It is an empty community
                final_sol.remove(com)
    
        return final_sol

    def change_to_random_community(communities, node):
        # Ahora, movemos node a uno aleatorio que no sea en el que se encuentra actualmente
        # Movemos el nodo de su comunidad actual a otra aleatoria

        dest_community_index = randrange(0,len(communities),1)
        while(dest_community_index == current_community_index):
            # print('coincide el random',dest_community_index,'ACTUAL:',current_community_index)
            dest_community_index = randrange(0,len(communities),1)
        
        # print('nodo',node,'pretende ir de comunidad',current_community_index,'a',dest_community_index)

        #Añadimos el nodo a destination_community y lo eliminamos el original:
        # print('comunidades originalmente',communities)
        #Copiamos las comunidades en len(communities) 'sets' en lugar de frozensets para poder añadir y
        # eliminar, aunque luego lo volveremos a convertir en frozenset

        communities_setted = [set(community) for community in communities]
        communities_setted[dest_community_index].add(node)
        communities_setted[current_community_index].remove(node)
        new_random_partition = [frozenset(community_setted) for community_setted in communities_setted]
        #HAY QUE TRATAR CUANDO SE QUEDA UNA COMUNIDAD VACÍA
        for com in new_random_partition:
            if len(com) == 0:# It is an empty community
                new_random_partition.remove(com)

        return new_random_partition
    
    return random.choice([change_to_random_community,create_new_community])(s_iter,node)

def explore_neighborhood(network, s_iter, s_best, tabu_moves, s_neigh, node_best):
    node_best = 0
    for node in network.nodes:
        s_move = solution_from_move(network, s_iter[:], node) #¿necesario introducir network?, creo que no (y de momento no se usa)

        if mymodularity(network,s_move) > mymodularity(network,s_best):
            tabu_moves[node] = 0
        
        if tabu_moves[node] == 0 and (node_best == 0 or mymodularity(network,s_move) > mymodularity(network,s_neigh)):
            node_best = node
            s_neigh = s_move[:]
    
    return tabu_moves, s_neigh, node_best

def tabu_modularity_optimization(network, s_init):

    tabu_tenure = 2 # maximo numero de iteraciones en los que un mismo movimiento no se puede repetir
    tabu_moves = [] #contador de movimientos prohibidos, las posiciones son el entero que representa al nodo y el valor es el numero de movimientos restantes para poder volver a moverlo (siendo el maximo, tabu_tenure)
    max_idle = 0 #max numero de iteraciones inactivas, posteriormente lo calculamos en funcion del tamaño del grafo
    num_idle = 0 #numero de iteraciones inactivas (AKA que no implican una mejora)
    s_iter = [] #solucion de la iteracion actual
    s_neigh = [] #solucion en el vecindario (neighbourhood)
    node_best = None #nodo con el mejor movimiento
   
    #Inicializamos
    tabu_moves = [0] * (max(network.nodes) + 1)
    max_idle = math.floor(max_of_nonimprovements(len(network.nodes)))
    # max_idle = 1
    num_idle = 0
    s_iter = s_init
    s_best = s_init
    vueltas = 0

    # print('maximo de vueltas inutiles',max_idle)
    while num_idle < max_idle:
        # print(vueltas,'VUELTAS')
        vueltas = vueltas + 1
        (tabu_moves, s_neigh, node_best) = explore_neighborhood(network, s_iter[:], s_best[:], tabu_moves[:], s_neigh[:], node_best)
        for node in network.nodes:
            #decrease the tabu moves 
            tabu_moves[node] = max(0,tabu_moves[node]-1) 
            
        tabu_moves[node_best] = tabu_tenure
        s_iter = s_neigh[:]
        if mymodularity(network, s_neigh[:]) > mymodularity(network, s_best[:]):
            s_best = s_neigh[:]
            num_idle = 0
        else:
            num_idle = num_idle + 1
        # print(num_idle)
    return s_best
    