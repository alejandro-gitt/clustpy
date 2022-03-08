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

#Creamos unas comunidades aleatorias, por ejemplo, los pares en una y los impares en otra

pares = frozenset([nodo for nodo in MDG.nodes if nodo%2 == 0])
impares = frozenset([nodo for nodo in MDG.nodes if nodo%2 != 0])

c = [pares,impares]
print(mymodularity(MDG,c))

optimized_communities = tabu_modularity_optimization(MDG,c)

print(mymodularity(MDG,optimized_communities))