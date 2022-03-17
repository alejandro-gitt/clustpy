import networkx as nx
import matplotlib.pyplot as plt
from numpy import partition
import pandas as pd
import copy
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

'''Funciones necesarias para dibujar el grafo'''

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
    # print(between_community_edges)
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


"""
Obtenemos los sexos de los nodos:
"""
def divide_by_gender(dict_node_gen):
    '''
    Input:
    Dictionary with the format: node: 'H'. For example:
    {125: 'H',111: 'M'}

    Returns:
    partition as in list made of two frozensets containing the male and female nodes.
    '''
    males = []
    females = []
    for node in dict_node_gen:
        if dict_node_gen[node] == 'H':
            males.append(node)
        elif dict_node_gen[node] == 'M':
            females.append(node)
        else:
            print('Ni H ni M')

    
    return [frozenset(males),frozenset(females)]
    

results_dict = {}
##CREAMOS UN MDG POR CADA CLASE QUE HAY
n_grados = df_nodes["Curso"].nunique()
for n in range(n_grados):
    j=n+1
    aulas = df_nodes[df_nodes["Curso"] == "%sº ESO" % j]['Grupo'].unique()
    n_aulas = df_nodes[df_nodes["Curso"] == "%sº ESO" % j]['Grupo'].nunique()

    for aula in aulas:
        alumnos_en_aula = df_nodes[df_nodes["Curso"] == "%sº ESO" % j][df_nodes["Grupo"] == "%s" % aula]['Nodes']
        sexos_en_aula = df_nodes[df_nodes["Curso"] == "%sº ESO" % j][df_nodes["Grupo"] == "%s" % aula]['Sexo']
        # lista_alumnos_en_aula = list(alumnos_en_aula)
        # lista_sexos_en_aula = list(sexos_en_aula)
        #Hacer aqui una lista de alumnos en aula?

        dict_alumnos_sexos = {} # guardamos nodo : 'H' / nodo : 'M'
        for i in range(len(list(alumnos_en_aula))):
            dict_alumnos_sexos[list(alumnos_en_aula)[i]] = list(sexos_en_aula)[i]
        
        fromtos = []
        for alumno in alumnos_en_aula:
            fromtos.append(list(zip(list(df_edges.loc[df_edges['from'] == alumno]['from']),list(df_edges.loc[df_edges['from'] == alumno]['to']),list(df_edges.loc[df_edges['from'] == alumno]['weight']))))
        enlaces_aula = [item for sublist in fromtos for item in sublist]
  
        enlaces_aula_filtrado = [(u,v,w) for (u,v,w) in enlaces_aula if v in list(alumnos_en_aula)] #Guardamos solo los enlaces que apunten fuera dentro de la clase

        MDGaula = nx.MultiDiGraph()
        # print('ALUMNOS EN AULA A PUNTO DE SER INTRODUCIDOS(%sº ESO %s:)'%(j,aula),list(alumnos_en_aula))
        # print('ENLACES A PUNTO DE SER INTRODUCIDOS (%sº ESO %s:)'%(j,aula),enlaces_aula)
        MDGaula.add_nodes_from(list(alumnos_en_aula))
        MDGaula.add_weighted_edges_from(enlaces_aula_filtrado)
        # print('resultado de add nodes from',MDGaula.nodes)
        results_dict["%sº ESO %s" % (j,aula)] = {'graph': MDGaula,'partition': None,'numero de alumnos': len(alumnos_en_aula) ,'alumnos con sexos': dict_alumnos_sexos,'init_modularity': None,'final_modularity': None,'by_gender_modularity': None,'gender_partition': None}


        

tiempos = []
mejoras_modularidad = []
string_clase = '1º ESO A'

for clase in list(results_dict.keys())[list(results_dict).index(string_clase):list(results_dict).index(string_clase)+1]:# (hay 21 clases). Como esta escrito solo saca la clase string_clase
    
    MDG_clase = results_dict[clase]['graph']
    pares = frozenset([nodo for nodo in MDG_clase.nodes if nodo%2 == 0])
    impares = frozenset([nodo for nodo in MDG_clase.nodes if nodo%2 != 0])
    c = [pares,impares]
    print(c)
    print('Longitud del grafo:',len(MDG_clase.nodes))
    # print('NODOS MDG CLASE',MDG_clase.nodes)
    results_dict[clase]['gender_partition'] = divide_by_gender(results_dict[clase]['alumnos con sexos'])
    results_dict[clase]['init_modularity'] = mymodularity(MDG_clase,c[:])
    # results_dict[clase]['by_gender_modularity'] = mymodularity(MDG_clase,results_dict[clase]['gender_partition'])
    start = time.time()
    print('tiempo inicial',start)
    optimized_communities = tabu_modularity_optimization(MDG_clase,c[:],max_idle = 0.2*results_dict[clase]['numero de alumnos'])
    end = time.time()
    print('tiempo final',end)
    results_dict[clase]['final_modularity'] =  mymodularity(MDG_clase, optimized_communities[:])
    results_dict[clase]['partition'] = optimized_communities
    
tiempos.append(end-start)

mejoras_modularidad.append(results_dict[string_clase]['final_modularity']/results_dict[string_clase]['init_modularity'] * 100)


####
g = results_dict[string_clase]['graph']
communities = results_dict[string_clase]['partition']
communities_genders  = results_dict[string_clase]['gender_partition']
# print('-------------------------RESULTADOS DE MODULARITY----------------------')
# print('MODULARIDAD CON TABU',mymodularity(g,communities))
# print('MODULARIDAD CON GENEROS',mymodularity(communities_genders))

community_counter = 0
communities_dict = {}
for comm in communities:
    for node in comm:
        communities_dict[node] = community_counter
    community_counter = community_counter +1

partition = communities_dict

pos = community_layout(g, partition)

list_colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
color_counter = 0 # for iterations
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
    edge_color='green'
)
nx.draw_networkx_edges(
    g,
    pos,
    edgelist=oneedges,
    width=1,
    alpha=0.5,
    edge_color='blue'
)
nx.draw_networkx_edges(
    g,
    pos,
    edgelist=neg_oneedges,
    width=1,
    alpha=0.5,
    edge_color='red'
)
nx.draw_networkx_edges(
    g,
    pos,
    edgelist=neg_twoedges,
    width=1,
    alpha=0.5,
    edge_color='purple'
)

plt.show()

#Ahora dibujamos, haciendo que las comunidades simplemente sean los sexos: