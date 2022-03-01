import matplotlib.pyplot as plt
import networkx as nx
from networkx.algorithms.community.community_utils import is_partition

G = nx.MultiDiGraph()
weight = 'weight'
communities = [frozenset({0, 1}), frozenset({2, 3})]
G.add_weighted_edges_from([(0, 1, 3.0), (1, 2, -4.0), (2,1, -7.0), (1,3,2.0)])
out_degree =  dict(G.out_degree(weight=weight))

# comm.add_weighted_edges_from([(0,1,3.0), (1, 2, -4.0)])
elarge = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] > 0]
esmall = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] <= 0]

pos = nx.spring_layout(G, seed=7)  # positions for all nodes - seed for reproducibility

# nodes
nx.draw_networkx_nodes(G, pos, node_size=700)

# edges
nx.draw_networkx_edges(G, pos, edgelist=elarge, width=6)
nx.draw_networkx_edges(
    G, pos, edgelist=esmall, width=6, alpha=0.5, edge_color="b", style="dashed"
)

# labels
nx.draw_networkx_labels(G, pos, font_size=20, font_family="sans-serif")

# ax = plt.gca()
# ax.margins(0.08)
# plt.axis("off")
# plt.tight_layout()
# plt.show()

weight = 'weight'

if not isinstance(communities, list):
    communities = list(communities)
if not is_partition(G, communities):
    print('notAPartition')

pos_total_weight = sum(wt for u, v, wt in G.edges(data = weight, default=1) if wt > 0) #Sum all positive links
neg_total_weight = sum(wt for u, v, wt in G.edges(data=weight, default=1) if wt < 0) #Sum all negative links


def community_contribution_negatively_weighted(community):
    comm = set(community)
    L_a = sum(wt for u, v, wt in G.edges(comm, data=weight, default=1) if v in comm) #L_c identical, sum of all weights within a community
    pos_degree_sum = sum(wt for u, v, wt in G.edges(comm, data=weight, default=1) if (v in comm and wt > 0))
    neg_degree_sum = sum(-wt for u, v, wt in G.edges(comm, data=weight, default=1) if (v in comm and wt < 0))# -wt porque tomamos los pesos con signo positivo

    return L_a - pos_degree_sum**2/(2*pos_total_weight) + neg_degree_sum**2/(2*neg_total_weight)

print( (1/(2*(pos_total_weight + neg_total_weight)))*sum(map(community_contribution_negatively_weighted, communities)) )

###
### Busco obtener dentro de la comunidad win+ wout+ win- wout- ###
###


#win+: Suma de todos los pesos positivos dentro de la comunidad alpha, entrantes a los nodos de dicha comunidad.
# Los grafos estan escritos de la forma (u(nodo origen),v(nodo destino),wt(peso del enlace)), por lo que si es entrante (in) tenemos que ver el wt de los nodos v para los nodos v dentro de la comunidad. Si este wt es mayor que cero, formará parte del conjunto que buscamos.

# for community in communities:
#     for node in community:
#         for u,v,wt in G.edges(community, data=weight, default=1):
#             if v in community:
#                 print('existen \'in'' en el nodo', v )
# print('')
# print('edges',G.edges(data = True))
# print('')
# print('IN_EDGES',G.in_edges(data = True))
# print('')

# for u, v, wt in G.edges(data = True): 
#     print('nodo destino',v)
#     if v in communities[1]:
#         print('En comunidad')

# for community in communities:
#     print(G.edges(community))# g.edges(community) devuelve lista de tuplas (u,v,wt) cuyo destino esta en community (v is in community)

community = list(communities[0])
print('the community is ',community)


w_out_all_comm = G.edges(community, data=weight, default=1)
print('all weights OUT the community: ',w_out_all_comm)
w_out_positive_comm = [wt for u,v,wt in w_out_all_comm if wt > 0]
print('positive weights out: ',w_out_positive_comm)
w_out_negative_comm = [wt for u,v,wt in w_out_all_comm if wt < 0]
print('negative weights out: ',w_out_negative_comm)

edges_all = G.edges(data = weight)
print('every edge on the Graph is: ',edges_all)

incident_weights_into_comm = [wt for u,v,wt in edges_all if v in community]
print('incident weights into the community are: ',incident_weights_into_comm)

incident_positive_weights_into_comm = [wt for u,v,wt in edges_all if v in community and wt > 0]
print('incident positive weights into the community are: ',incident_positive_weights_into_comm)

incident_negative_weights_into_comm = [wt for u,v,wt in edges_all if v in community and wt<0]
print('incident negative weights into the community are: ',incident_negative_weights_into_comm)
