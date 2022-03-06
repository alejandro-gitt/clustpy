import matplotlib.pyplot as plt
import networkx as nx
# from networkx.algorithms.community.community_utils import is_partition
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
show_mygraph(G,communities)

print('optimizacion con tabu search:')
particion_optimizada = tabu_modularity_optimization(G,communities)
show_mygraph(G,particion_optimizada)
print('MODULARIDAD OPTIMIZADA CON TABU SEARCH:', mymodularity(G,particion_optimizada))