import matplotlib.pyplot as plt
import networkx as nx
from networkx.algorithms.community.community_utils import is_partition
from mymod import mymodularity
from tabusearch import tabu_modularity_optimization
from tabusearch import find_nodes_community
from random import randrange

G = nx.MultiDiGraph()
weight = 'weight'
communities = [frozenset({0, 1}), frozenset({2, 3})]
G.add_weighted_edges_from([(0, 1, 3.0), (1, 2, -4.0), (2,1, -7.0), (1,3,2.0)])
out_degree =  dict(G.out_degree(weight=weight))


def show_mygraph(G,communities,weight='weight'):

    elarge = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] > 0]
    esmall = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] <= 0]
    pos = nx.spiral_layout(G)  # positions for all nodes - seed for reproducibility

    # nodes
    color_map = []
    for node in G:
        if node in communities[0]:
            color_map.append('blue')
        else: 
            color_map.append('pink')     
            
    nx.draw_networkx_nodes(G, pos, node_color=color_map, node_size=700)
    # edges
    nx.draw_networkx_edges(G, pos ,edgelist=elarge,edge_color="g", width=6,connectionstyle='angle3')
    nx.draw_networkx_edges(
        G, pos, edgelist=esmall, width=6, edge_color="red",connectionstyle='angle3')

    # labels
    nx.draw_networkx_labels(G, pos, font_size=20, font_family="sans-serif")
    nx.draw_networkx_edge_labels(
        G, pos,
        edge_labels={(0, 1): '3.0',(1, 3): '2.0'},
        font_color='green'
    )
    nx.draw_networkx_edge_labels(
        G, pos,
        edge_labels={(1, 2): '-4.0',(2, 1): '-7.0' },
        font_color='red'
    )

    ax = plt.gca()
    ax.margins(0.08)
    plt.axis("off")
    plt.show()

show_mygraph(G,communities)
print('MODULARIDAD',mymodularity(G,communities))
#quiero mover nodo de una comunidad a otra aleatoria.
#- Si no hay mas comunidades (solo existe 1), crear una nueva e introducir el nodo en la misma
node = 1
if len(communities) <= 1:
    #Debemos crear una nueva comunidad en la que introducir el nodo
    print('Solo existe una comunidad o ninguna, creamos una nueva que solo contenga al nodo')
    communities.append(frozenset({node}))
else:
    # Movemos el nodo de su comunidad actual a otra aleatoria
    print('originalmente',communities)
    current_community_index = find_nodes_community(communities, node) #INDICE
    dest_community_index = randrange(0,len(communities),1)
    while(dest_community_index == current_community_index):
        # print('coincide el random',dest_community_index,'ACTUAL:',current_community_index)
        dest_community_index = randrange(0,len(communities),1)
    
    print('nodo',node,'pretende ir de comunidad',current_community_index,'a',dest_community_index)

    #Añadimos el nodo a destination_community y lo eliminamos el original:
    print('comunidades originalmente',communities)
    #Copiamos las comunidades en len(communities) 'sets' en lugar de frozensets para poder añadir y
    # eliminar, aunque luego lo volveremos a convertir en frozenset

    communities_setted = [set(community) for community in communities]
    communities_setted[dest_community_index].add(node)
    communities_setted[current_community_index].remove(node)
    communities = [frozenset(community_setted) for community_setted in communities_setted]

    print('comunidades finalmente',communities)

show_mygraph(G,communities)

print('optimizacion con tabu search:')
particion_optimizada = tabu_modularity_optimization(G,communities)
show_mygraph(G,particion_optimizada)
print('MODULARIDAD OPTIMIZADA:', mymodularity(G,particion_optimizada))