import matplotlib.pyplot as plt
import networkx as nx
from networkx.algorithms.community.community_utils import is_partition

G = nx.MultiDiGraph()
weight = 'weight'
communities = [frozenset({0, 1}), frozenset({2, 3})]
G.add_weighted_edges_from([(0, 1, 3.0), (1, 2, -4.0), (2,1, -7.0), (1,3,2.0)])
out_degree =  dict(G.out_degree(weight=weight))

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

weight = 'weight'

if not isinstance(communities, list):
    communities = list(communities)
if not is_partition(G, communities):
    print('notAPartition')

pos_total_weight = sum(wt for u, v, wt in G.edges(data = weight, default=1) if wt > 0) #Sum all positive links
neg_total_weight = sum(-wt for u, v, wt in G.edges(data=weight, default=1) if wt < 0) #Sum all negative links


def community_contribution_directed_negatively_weighted(community):
    comm = set(community)
    L_a = sum(wt for u, v, wt in G.edges(comm, data=weight, default=1) if v in comm)
    w_out_positive_comm = sum(wt for u,v,wt in G.edges(community, data=weight, default=1) if wt > 0)
    w_out_negative_comm = sum(-wt for u,v,wt in G.edges(community, data=weight, default=1) if wt < 0)
    w_in_all_comm = [wt for u,v,wt in G.edges( data=weight, default=1) if v in community]
    w_in_positive_comm = sum(wt for u,v,wt in G.edges( data=weight, default=1) if v in community and wt > 0)
    w_in_negative_comm = sum(-wt for u,v,wt in G.edges( data=weight, default=1) if v in community and wt < 0)
    
    return L_a - (w_in_positive_comm*w_out_positive_comm)/(2*pos_total_weight) + (w_in_negative_comm*w_out_negative_comm)/(2*neg_total_weight)


result  = (1/(2*(pos_total_weight + neg_total_weight)))*sum(map(community_contribution_directed_negatively_weighted, communities))
print(result)

# edges_out_all_comm = G.edges(community, data=weight, default=1)
# print('all weights OUT the community: ',edges_out_all_comm)
# w_out_positive_comm = [wt for u,v,wt in edges_out_all_comm if wt > 0]
# print('positive weights out: ',w_out_positive_comm)
# w_out_negative_comm = [wt for u,v,wt in edges_out_all_comm if wt < 0]
# print('negative weights out: ',w_out_negative_comm)

# edges_all = G.edges(data = weight)
# print('every edge on the Graph is: ',edges_all)

# w_in_all_comm = [wt for u,v,wt in edges_all if v in community]
# print('incident weights into the community are: ',w_in_all_comm)

# w_in_positive_comm = [wt for u,v,wt in edges_all if v in community and wt > 0]
# print('incident positive weights into the community are: ',w_in_positive_comm)

# w_in_negative_comm = [wt for u,v,wt in edges_all if v in community and wt<0]
# print('incident negative weights into the community are: ',w_in_negative_comm)

# w_all_comm = sum(w_out_positive_comm) + sum(w_out_negative_comm) + sum(w_in_all_comm)

# print('Lalpha = ',w_all_comm)
