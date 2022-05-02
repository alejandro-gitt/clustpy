import networkx as nx
import numpy as np
import matplotlib.cm
import matplotlib.pyplot as plt
from numpy import partition
import pandas as pd
import matplotlib.colors
import matplotlib.cm
from mymod import mymodularity
from tabusearch import tabu_modularity_optimization
import time
import matplotlib.patches as mpatches
from matplotlib.axes._axes import _log as matplotlib_axes_logger
matplotlib_axes_logger.setLevel('ERROR')


nodes_path = r'.\Nodes_t1.csv' 
edges_path = r'.\Edges_t1.csv'
df_nodes = pd.read_csv(nodes_path, sep=';', encoding='unicode_escape')
df_edges = pd.read_csv(edges_path, sep=';', encoding='unicode_escape')

'''
Functions for drawing:
'''

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

'''
Functions with algorithmic purposes:
'''

def divide_by_gender(dict_node_gen):
    '''
    Input:
    Dictionary with the format: node: 'H'. For example:
    {125: 'H',111: 'M'}
    Being 'H' = Hombre (male) and 'M' = Mujer (female)

    Returns:
    Partition as in list made of two frozensets containing the male and female nodes respectively.
    '''
    males = []
    females = []
    for node in dict_node_gen:
        if dict_node_gen[node] == 'H':
            males.append(node)
        elif dict_node_gen[node] == 'M':
            females.append(node)
        else:
            raise ValueError(
                'Values of input dictionary should be either H or M, but it is \'%s\'' % dict_node_gen[node])

    return [frozenset(males), frozenset(females)]


def n_times_tabu(graph, s_init, ntimes=1, max_idle=1):
    '''
    Applies tabu modularity optimization n times. 
    For an improved functioning, it takes the result of the (i-1) iteration as the input for the (i) iteration.
    Also, it stores and returns only the best result of all the iterations.

    Parameters
    ----------
    graph : Networkx MultiDiGraph which contains nodes and edges that may be positively or negatively weighted
    
    s_init: Initial solution AKA partition as a list of sets, being each set a different community

    ntimes : Integer which determines the amount of times the algorithm will be executed sequentially.
    node to be found in one of the communities given

    max_idle : Number of maximum permitted idle moves by tabu (see tabu search)
    
    Returns
    -------
    best_resulting_partition : Best partition obtained out of the n iterations
    '''

    # Vemos la modularidad con la que empezamos:
    # We first check the initial modularity:
    best_mod = mymodularity(graph, s_init[:])
    print('starting modularity', best_mod)
    best_resulting_partition = s_init

    # Ahora aplicamos tabu y vemos si alguna de las particiones de ahora en adelante mejora esta modularidad inicial
    # We now apply tabu and check if any oof the partitions from now on improves this inital Q
    for i in range(ntimes):
        s_iter = tabu_modularity_optimization(
            graph, s_init[:], max_idle=max_idle)

        # Vemos si ha mejorado la Q y si es el caso, guardamos esta partición:
        # If Q improved, we store this partition:
        iter_mod = mymodularity(graph, s_iter[:])
        if iter_mod > best_mod:
            best_resulting_partition = s_iter
            best_mod = iter_mod

    return best_resulting_partition


'''
Script:
In this case, we have different classrooms with its students.
nodes: Students
edges: Relationship between mapped students as -2, -1, 1, 2 being -2 a really negative relationship (enemies) and +2 a really positive one (friends)

We have stored the nodes and edges in Pandas dataframes and we can access them.
'''

'''
1. We create a Networkx MultiDiGraph for each classroom.
In order to have a compact way of saving data about each classroom we'll create a dictionary that contains:

- 'graph': MultiDiGraph created with the edges and nodes of a classroom
- 'partition': Initallized as None, it is for the posterior saving of the groups or clusters found by algorithms made for partitioning networks (such as tabu)
- 'numero de alumnos': Number of students in the classroom,
- 'alumnos con sexos': A special dictionary that stores for every node, its gender. Gender is given in the dataframe and now is stored as: " nodeID: 'H'/'M' " 
- 'init_modularity': Initallized as None, it's the original modularity obtained by the original graph partitioned randomly
- 'final_modularity': Initallized as None, it's the resulting modularity after the graph has been through a communities detection algorithm
- 'by_gender_modularity': Initallized as None, it's the modularity we obtain if we divide just in two clusters: male and female students
- 'gender_partition': Initallized as None, it is a list of sets, being each set a different community, in this case: set of males and set of females

'''
results_dict = {}
n_grados = df_nodes["Curso"].nunique()

for n in range(n_grados):
    j = n+1
    aulas = df_nodes[df_nodes["Curso"] == "%sº ESO" % j]['Grupo'].unique()
    n_aulas = df_nodes[df_nodes["Curso"] == "%sº ESO" % j]['Grupo'].nunique()

    for aula in aulas:
        alumnos_en_aula = df_nodes[df_nodes["Curso"] == "%sº ESO" %
                                   j][df_nodes["Grupo"] == "%s" % aula]['Nodes']
        sexos_en_aula = df_nodes[df_nodes["Curso"] == "%sº ESO" %
                                 j][df_nodes["Grupo"] == "%s" % aula]['Sexo']

        dict_alumnos_sexos = {}  # storing node : 'H' / node : 'M'
        for i in range(len(list(alumnos_en_aula))):
            dict_alumnos_sexos[list(alumnos_en_aula)[i]
                               ] = list(sexos_en_aula)[i]

        fromtos = []
        for alumno in alumnos_en_aula:
            fromtos.append(list(zip(list(df_edges.loc[df_edges['from'] == alumno]['from']), list(
                df_edges.loc[df_edges['from'] == alumno]['to']), list(df_edges.loc[df_edges['from'] == alumno]['weight']))))
        enlaces_aula = [item for sublist in fromtos for item in sublist]

        # Storing exclusively the edges that start and finish inside the community
        enlaces_aula_filtrado = [(u, v, w) for (
            u, v, w) in enlaces_aula if v in list(alumnos_en_aula)]

        MDGaula = nx.MultiDiGraph()
        MDGaula.add_nodes_from(list(alumnos_en_aula))
        MDGaula.add_weighted_edges_from(enlaces_aula_filtrado)

        # Dict for storing the different
        results_dict["%sº ESO %s" % (j, aula)] = {'graph': MDGaula, 'partition': None, 'numero de alumnos': len(alumnos_en_aula),
                                                  'alumnos con sexos': dict_alumnos_sexos, 'init_modularity': None, 'final_modularity': None,
                                                  'by_gender_modularity': None, 'gender_partition': None}

'''
2. Processing the graphs

Now, we separate by genders, apply algorithms and get modularity values and store it at the dictionaries
'''

'''
Note: As it is currently written, it will apply the processing chunk to every classrooms' graph. This could lead to undesired execution times.
In case you want to see a quicker example, pleas uncomment the next three lines and comment the fourth as well as the first two lines in next step (3.).
This will just target a single (or n_clases_a_procesar) graph and will process and draw it.
'''
# string_clase = '2º ESO B'#Uncomment if processing takes too long
# n_clases_a_procesar = 1  #Uncomment if processing takes too long
# for clase in list(results_dict.keys())[list(results_dict).index(string_clase):list(results_dict).index(string_clase)+n_clases_a_procesar]: #Uncomment if processing takes too long
for clase in list(results_dict.keys()): #COMMENT if processing takes too long
    MDG_clase = results_dict[clase]['graph']
    print('Graph\'s length:', len(MDG_clase.nodes))

    # Our initial partition will be based on genders:

    # Dividing by gender and storing the initial modularity value (Initial partition could be any)
    results_dict[clase]['gender_partition'] = divide_by_gender(
        results_dict[clase]['alumnos con sexos'])

    results_dict[clase]['by_gender_modularity'] = mymodularity(
        MDG_clase, results_dict[clase]['gender_partition'])

    # Initialize values before we apply tabu
    c = results_dict[clase]['gender_partition']
    results_dict[clase]['init_modularity'] = results_dict[clase]['by_gender_modularity']

    # Applying tabu modularity optimization for optimizing communities:
    start = time.time()
    optimized_communities = n_times_tabu(
        MDG_clase, c[:], ntimes=10, max_idle=0.5*results_dict[clase]['numero de alumnos'])
    end = time.time()
    print('Done in ', end-start, 's')

    # Storing resulting partition and modularity value
    results_dict[clase]['final_modularity'] = mymodularity(
        MDG_clase, optimized_communities[:])
    results_dict[clase]['partition'] = optimized_communities

'''
3. Drawing the graphs
Finally just some preprocessing and work to be done in order to just draw the graphs separated into communities, please note:
- Node colors represent different communities
- Edges colors represent different weights (as explained in the legend)
'''
#for clase in list(results_dict.keys())[list(results_dict).index(string_clase):list(results_dict).index(string_clase)+n_clases_a_procesar]: #Uncomment if processing takes too long
for clase in list(results_dict.keys()): #COMMENT if processing takes too long
    g = results_dict[clase]['graph']
    communities = results_dict[clase]['partition']
    communities_genders = results_dict[clase]['gender_partition']

    community_counter = 0
    communities_dict = {}
    for comm in communities:
        for node in comm:
            communities_dict[node] = community_counter
        community_counter = community_counter + 1

    counter = 0
    communities_gender_dict = {}
    for comm in communities_genders:
        for node in comm:
            communities_gender_dict[node] = counter
        counter = counter + 1

    pos = community_layout(g, communities_dict)
    pos_genders = community_layout(g, communities_gender_dict)
    ## Mejora de apariencia ##
    cmap = matplotlib.cm.get_cmap('cool')
    list_colors = [matplotlib.colors.to_hex(list(cmap(comm_color))) for comm_color in np.linspace(
        0, 1, len(communities))]  # A hex porque en rgba no funcionaba bien

    # list_colors = ['#1f22b4', '#ff7f0e', '#2ca02c', '#d62728','#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']

    color_counter = 0  # for iterations
    black_patch = mpatches.Patch(color='black', label='-2')
    red_patch = mpatches.Patch(color='red', label='-1')
    blue_patch = mpatches.Patch(color='blue', label='1')
    green_patch = mpatches.Patch(color='green', label='2')

# Tabu results figures:

    plt.figure()

    for comm in communities:
        communities_nodes = []
        for node in list(comm):
            communities_nodes.append(node)
        # For each community we call draw_networkx_nodes
        nx.draw_networkx_nodes(
            g, pos, nodelist=communities_nodes, node_color=list_colors[color_counter])
        nx.draw_networkx_labels(g, pos, alpha=0.65, font_size=8)
        color_counter = color_counter + 1

    twoedges = []
    oneedges = []
    neg_oneedges = []
    neg_twoedges = []

    for edge in g.edges(data=True):
        edge_weight = edge[2]['weight']  # Get edge's weight
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
        alpha=0.2,
        connectionstyle='angle3',
        edge_color='green'
    )
    nx.draw_networkx_edges(
        g,
        pos,
        edgelist=oneedges,
        width=1,
        alpha=0.2,
        connectionstyle='angle3',
        edge_color='blue'
    )
    nx.draw_networkx_edges(
        g,
        pos,
        edgelist=neg_oneedges,
        width=1,
        alpha=0.2,
        connectionstyle='angle3',
        edge_color='red'
    )
    nx.draw_networkx_edges(
        g,
        pos,
        edgelist=neg_twoedges,
        width=1,
        alpha=0.2,
        connectionstyle='angle3',
        edge_color='black'
    )

    plt.legend(handles=[black_patch, red_patch, blue_patch, green_patch])
    plt.title('Communities by tabu (%s) modularity: %s' %
              (clase, results_dict[clase]['final_modularity']))
    plt.savefig('Tabu(%s).png' % clase, dpi=300, bbox_inches='tight')

# Simply by genders figures

    plt.figure()

    color_counter = 0  # for iterations
    for comm in communities_genders:
        communities_nodes = []
        for node in list(comm):
            communities_nodes.append(node)
        # Por cada comunidad llamamos a draw nodes
        nx.draw_networkx_nodes(
            g, pos_genders, nodelist=communities_nodes, node_color=list_colors[color_counter])
        nx.draw_networkx_labels(g, pos_genders, alpha=0.75, font_size=9)
        color_counter = color_counter + 1

    nx.draw_networkx_edges(
        g,
        pos_genders,
        edgelist=twoedges,
        width=1,
        alpha=0.2,
        connectionstyle='arc3,rad=0.5',
        edge_color='green',
        label='2'
    )
    nx.draw_networkx_edges(
        g,
        pos_genders,
        edgelist=oneedges,
        width=1,
        alpha=0.2,
        connectionstyle='arc3,rad=0.5',
        edge_color='blue',
        label='1'
    )
    nx.draw_networkx_edges(
        g,
        pos_genders,
        edgelist=neg_oneedges,
        width=1,
        alpha=0.2,
        connectionstyle='arc3,rad=0.5',
        edge_color='red',
        label='-1'
    )
    nx.draw_networkx_edges(
        g,
        pos_genders,
        edgelist=neg_twoedges,
        width=1,
        alpha=0.2,
        connectionstyle='arc3,rad=0.5',
        edge_color='black',
        label='-2'
    )
    plt.title('Communities by gender (%s) modularity: %s' %
              (clase, results_dict[clase]['by_gender_modularity']))
    plt.legend(handles=[black_patch, red_patch, blue_patch, green_patch])
    plt.savefig('By gender(%s).png' % clase, dpi=300, bbox_inches='tight')
    plt.show()