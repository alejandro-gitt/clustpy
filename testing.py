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

c = community.modularity_max.greedy_modularity_communities(MDG)

# Busco la comunidad en la que se encuentra el nodo 'target'
# i = 0
# target = 1032

# if not any([target in comm for comm in c]):
#     print('TARGET NODE NOT FOUND IN ANY OF THE COMMUNITIES')

# #node found in a community, lets see which one:

# for community in c:
    
#     if any([target in community]):
#         print('nodo',target,'encontrado en comunidad', i)
    
#     i = i+1 
print(min(MDG.nodes))
print(max(MDG.nodes))
moves = [0] * (max(MDG.nodes)+1)

moves[593] = 292929
print(moves[599])

# for node in MDG.nodes:
#     print(moves[node])