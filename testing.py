import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
from random import randint
# For color mapping
import matplotlib.colors as colors
import matplotlib.cm as cmx
from networkx.algorithms import community
import networkx.algorithms.community as nx_comm
from mymod import mymodularity
from tabusearch import tabu_modularity_optimization
nodes_path = r'C:\Users\proal\Documents\UC3M\2021-2022\2\TFG\algoritmo1\datos\Nodes_t1.csv'
edges_path = r'C:\Users\proal\Documents\UC3M\2021-2022\2\TFG\algoritmo1\datos\Edges_t1.csv'
df_nodes = pd.read_csv(nodes_path, sep = ';',encoding='unicode_escape')
df_edges = pd.read_csv(edges_path, sep = ';',encoding='unicode_escape')
MDG = nx.MultiDiGraph()
MDG.add_nodes_from(df_nodes['Nodes'])

tuples_from_to = []
for i in range(len(df_edges)):
    tuples_from_to.append((df_edges['from'][i],df_edges['to'][i],df_edges['weight'][i]))
MDG.add_weighted_edges_from(tuples_from_to)

results_dict = {}

##CREAMOS UN MDG POR CADA CLASE QUE HAY
n_grados = df_nodes["Curso"].nunique()
grafos = []
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
        grafos.append(MDGaula)
        results_dict["%sº ESO %s" % (j,aula)] = {'graph': MDGaula, 'init_modularity': None,'final_modularity': None}

# for MDG_clase in grafos:
# #Creamos unas comunidades aleatorias, por ejemplo, los pares en una y los impares en otra

#     pares = frozenset([nodo for nodo in MDG_clase.nodes if nodo%2 == 0])
#     impares = frozenset([nodo for nodo in MDG_clase.nodes if nodo%2 != 0])
#     c = [pares,impares]

#     print(MDG_clase)
#     print(MDG_clase.nodes)
#     modularidad_antes = mymodularity(MDG_clase,c[:])

#     print('MODULARIDAD ANTES',modularidad_antes)

#     optimized_communities = tabu_modularity_optimization(MDG_clase,c[:])

#     print('MODULARIDAD OPTIMIZADA',mymodularity(MDG_clase,optimized_communities[:]))

for clase in list(results_dict.keys())[19:20]:
    
    MDG_clase = results_dict[clase]['graph']
    pares = frozenset([nodo for nodo in MDG_clase.nodes if nodo%2 == 0])
    impares = frozenset([nodo for nodo in MDG_clase.nodes if nodo%2 != 0])
    c = [pares,impares]

    results_dict[clase]['init_modularity'] = mymodularity(MDG_clase,c[:])
    optimized_communities = tabu_modularity_optimization(MDG_clase,c[:])
    results_dict[clase]['final_modularity'] =  mymodularity(MDG_clase, optimized_communities[:])

print(results_dict)