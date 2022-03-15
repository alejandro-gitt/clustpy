import networkx as nx
import matplotlib.pyplot as plt
from numpy import partition
import pandas as pd
from random import randint
# For color mapping
import matplotlib.colors as colors
import matplotlib.cm as cmx
from networkx.algorithms import community
import networkx.algorithms.community as nx_comm
from mymod import mymodularity
from tabusearch import tabu_modularity_optimization
import time
from netgraph import Graph


nodes_path = r'C:\Users\proal\Documents\UC3M\2021-2022\2\TFG\algoritmo1\datos\Nodes_t1.csv'
edges_path = r'C:\Users\proal\Documents\UC3M\2021-2022\2\TFG\algoritmo1\datos\Edges_t1.csv'
df_nodes = pd.read_csv(nodes_path, sep = ';',encoding='unicode_escape')
df_edges = pd.read_csv(edges_path, sep = ';',encoding='unicode_escape')
MDG = nx.MultiDiGraph()
MDG.add_nodes_from(df_nodes['Nodes'])

"""
Dibujamos grafo de aula con distinción de colores por comunidades
"""
def show_mygraph(G,communities,weight='weight'):

    elarge = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] > 0]
    esmall = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] <= 0]
    pos = nx.shell_layout(G)  # positions for all nodes - seed for reproducibility

    # nodes
    color_map = []
    list_of_colors = ['blue','pink','green','red','yellow']
    
    i=0
    for node in G:
        for comm in communities:
            if node in comm:
                color_map.append(list_of_colors[i])
                i = i+1 

            
    nx.draw_networkx_nodes(G, pos, node_color=color_map, node_size=700)
    # edges
    nx.draw_networkx_edges(G, pos ,edgelist=elarge,edge_color="g", width=6,connectionstyle='angle3')
    nx.draw_networkx_edges(
        G, pos, edgelist=esmall, width=6, edge_color="red",connectionstyle='angle3')

    # labels
    nx.draw_networkx_labels(G, pos, font_size=20, font_family="sans-serif")
    #Legend
    cNorm = colors.Normalize(vmin = -2, vmax = 2)
    scalarMap = cmx.ScalarMappable(norm = cNorm, cmap = plt.cm.RdBu)
    ColorLegend = {'negativo fuerte': -2, 
            'negativo débil': -1, 
            'positivo fuerte': 2, 
            'positivo débil': 1}


    f = plt.figure(1)
    ax = f.add_subplot(1,1,1)
    for label in ColorLegend:
        ax.plot([0],[0],color=scalarMap.to_rgba(ColorLegend[label]),label=label)
    plt.title('Tabú')
    plt.legend(loc = 'lower right')
    nx.draw_shell(G,node_size=10,width = 0.1,vmin = -2, vmax = 2, edge_color = [-2,-1,1,2] ,edge_cmap=plt.cm.RdBu,ax=ax)
    
    plt.show()




#########
    """
    Compute the layout for a modular graph.


    Arguments:
    ----------
    g -- networkx.Graph or networkx.DiGraph instance
        graph to plot

    partition -- dict mapping int node -> int community
        graph partitions


    Returns:
    --------
    pos -- dict mapping int node -> (float x, float y)
        node positions

    """

    pos_communities = _position_communities(g, partition, scale=3.)

    pos_nodes = _position_nodes(g, partition, scale=1.)

    # combine positions
    pos = dict()
    for node in g.nodes():
        pos[node] = pos_communities[node] + pos_nodes[node]

    return pos


    # create a weighted graph, in which each node corresponds to a community,
    # and each edge weight to the number of edges between communities
    between_community_edges = _find_between_community_edges(g, partition)

    communities = set(partition.values())
    hypergraph = nx.DiGraph()
    hypergraph.add_nodes_from(communities)
    for (ci, cj), edges in between_community_edges.items():
        hypergraph.add_edge(ci, cj, weight=len(edges))

    # find layout for communities
    pos_communities = nx.spring_layout(hypergraph, **kwargs)

    # set node positions to position of community
    pos = dict()
    for node, community in partition.items():
        pos[node] = pos_communities[community]

    return pos

##########

"""
"""
results_dict = {}

##CREAMOS UN MDG POR CADA CLASE QUE HAY
n_grados = df_nodes["Curso"].nunique()
for i in range(n_grados):
    j=i+1
    aulas = df_nodes[df_nodes["Curso"] == "%sº ESO" % j]['Grupo'].unique()
    n_aulas = df_nodes[df_nodes["Curso"] == "%sº ESO" % j]['Grupo'].nunique()

    # print(n_aulas,'aulas en %sº ESO' % j )
    # print('AULAS:',aulas)
    for aula in aulas:
        newMDG = nx.MultiDiGraph()
        alumnos_en_aula = df_nodes[df_nodes["Curso"] == "%sº ESO" % j][df_nodes["Grupo"] == "%s" % aula]['Nodes']

        fromtos = []
        for alumno in alumnos_en_aula:
            fromtos.append(list(zip(list(df_edges.loc[df_edges['from'] == alumno]['from']),list(df_edges.loc[df_edges['from'] == alumno]['to']),list(df_edges.loc[df_edges['from'] == alumno]['weight']))))
        enlaces_aula = [item for sublist in fromtos for item in sublist]

        MDGaula = nx.MultiDiGraph()
        MDGaula.add_nodes_from(alumnos_en_aula)
        MDGaula.add_weighted_edges_from(enlaces_aula)
        results_dict["%sº ESO %s" % (j,aula)] = {'graph': MDGaula,'partition': None,'numero de alumnos': len(alumnos_en_aula) ,'init_modularity': None,'final_modularity': None}

tiempos = []
mejoras_modularidad = []

string_clase = '1º ESO A'

for clase in list(results_dict.keys())[list(results_dict).index(string_clase):list(results_dict).index(string_clase)+1]:# (hay 21 clases). Como esta escrito solo saca la clase string_clase
    
    MDG_clase = results_dict[clase]['graph']
    pares = frozenset([nodo for nodo in MDG_clase.nodes if nodo%2 == 0])
    impares = frozenset([nodo for nodo in MDG_clase.nodes if nodo%2 != 0])
    c = [pares,impares]

    results_dict[clase]['init_modularity'] = mymodularity(MDG_clase,c[:])

    start = time.time()
    optimized_communities = tabu_modularity_optimization(MDG_clase,c[:],max_idle = 0.2*results_dict[clase]['numero de alumnos'])
    end = time.time()
    
    results_dict[clase]['final_modularity'] =  mymodularity(MDG_clase, optimized_communities[:])
    results_dict[clase]['partition'] = optimized_communities

tiempos.append(end-start)

mejoras_modularidad.append(results_dict[string_clase]['final_modularity']/results_dict[string_clase]['init_modularity'] * 100)
print('Las',len(results_dict[string_clase]['partition']),'comunidades decididas son:')
print(results_dict[string_clase]['partition'])


def community_layout(g, partition):
    """
    Compute the layout for a modular graph.


    Arguments:
    ----------
    g -- networkx.Graph or networkx.DiGraph instance
        graph to plot

    partition -- dict mapping int node -> int community
        graph partitions


    Returns:
    --------
    pos -- dict mapping int node -> (float x, float y)
        node positions

    """

    pos_communities = _position_communities(g, partition, scale=3.)

    pos_nodes = _position_nodes(g, partition, scale=1.)

    # combine positions
    pos = dict()
    for node in g.nodes():
        pos[node] = pos_communities[node] + pos_nodes[node]

    return pos

def _position_communities(g, partition, **kwargs):

    # create a weighted graph, in which each node corresponds to a community,
    # and each edge weight to the number of edges between communities
    between_community_edges = _find_between_community_edges(g, partition)
    communities = set(partition.values())
    print(between_community_edges)
    # hypergraph = nx.DiGraph()
    hypergraph = nx.MultiDiGraph()
    hypergraph.add_nodes_from(communities)
    for (ci, cj), edges in between_community_edges.items():
        hypergraph.add_edge(ci, cj, weight=len(edges))

    # find layout for communities
    pos_communities = nx.spring_layout(hypergraph, **kwargs)

    # set node positions to position of community
    pos = dict()
    for node, community in partition.items():
        pos[node] = pos_communities[community]

    return pos

def _find_between_community_edges(g, partition):

    edges = dict()

    for (ni, nj) in g.edges():
        ci = partition[ni]
        cj = partition[nj]

        if ci != cj:
            try:
                edges[(ci, cj)] += [(ni, nj)]
            except KeyError:
                edges[(ci, cj)] = [(ni, nj)]
    return edges

def _position_nodes(g, partition, **kwargs):
    """
    Positions nodes within communities.
    """

    communities = dict()
    for node, community in partition.items():
        try:
            communities[community] += [node]
        except KeyError:
            communities[community] = [node]

    pos = dict()
    for ci, nodes in communities.items():
        subgraph = g.subgraph(nodes)
        pos_subgraph = nx.shell_layout(subgraph, **kwargs)
        pos.update(pos_subgraph)

    return pos



####


####
g = results_dict[string_clase]['graph']
communities = results_dict[string_clase]['partition']
list_tuples_node_community_id = []
community_counter = 0


communities_dict = {}
community_counter = 0

for comm in communities:
    for node in comm:
        communities_dict[node] = community_counter
    community_counter = community_counter +1

partition = communities_dict
node_to_community = communities_dict

flat_communities = [item for sublist in [list(x) for x in communities] for item in sublist]
for u,v in g.edges(data = False):
    if not v in flat_communities:
        # Eliminamos el edge de la red, ya que apunta a un alumno fuera
        g.remove_edge(u,v)


# partition tiene que ser un dict

pos = community_layout(g, partition)

# print(partition)
# print(partition.values())
# list_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
# color_map = []
# ccounter = 0 
# for comm in [list(x) for x in communities]:
#     for node in comm:
#         if node in comm:
#             color_map.append(list_colors[ccounter])
#     ccounter = ccounter +1 

# list_colors = ['tab:red','tab:green','tab:yellow','tab:blue','tab:pink']
list_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
color_counter = 0
for comm in communities:
    communities_nodes = []
    for node in list(comm):
        communities_nodes.append(node)
    #Por cada comunidad llamamos a draw nodes
    nx.draw_networkx_nodes(g, pos, nodelist=communities_nodes, node_color = list_colors[color_counter])
    nx.draw_networkx_labels(g, pos,alpha = 0.75, font_size= 9)
    color_counter = color_counter + 1
# nx.draw_networkx_nodes(g, pos, nodelist=[4, 5, 6, 7], node_color="tab:blue", **options)


twoedges = []
oneedges =[]
neg_oneedges = []
neg_twoedges = []

for edge in g.edges(data = True):
    edge_weight = edge[2]['weight'] # Con esto cogemos el peso del edge
    if edge_weight == 2:
        twoedges.append(edge)
    if edge_weight == 1:
        oneedges.append(edge)
    if edge_weight == -1:
        neg_oneedges.append(edge)
    if edge_weight == -2:
        neg_twoedges.append(edge)

nx.draw_networkx_edges(
    g,
    pos,
    edgelist=twoedges,
    width=1,
    alpha=0.5,
    edge_color='g'
)
nx.draw_networkx_edges(
    g,
    pos,
    edgelist=oneedges,
    width=1,
    alpha=0.5,
    edge_color='b'
)
nx.draw_networkx_edges(
    g,
    pos,
    edgelist=neg_oneedges,
    width=1,
    alpha=0.5,
    edge_color='r'
)
nx.draw_networkx_edges(
    g,
    pos,
    edgelist=neg_twoedges,
    width=1,
    alpha=0.5,
    edge_color='purple'
)


# nx.draw_networkx_edges(
#     g,
#     pos,
#     edgelist=g.edges(data = False),
#     width=1,
#     alpha=0.5
# )

# nx.draw(g, pos,with_labels = True,node_color = color_map)
plt.show()
