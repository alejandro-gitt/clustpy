from mymod import mymodularity
import networkx as nx

G = nx.MultiDiGraph()
G.add_nodes_from([405,
407,
409,
411,406,
408,
410])

G.add_weighted_edges_from([(411, 405, 2),(411, 406, -2),(411, 407, 2),(411, 408, -2),(411, 409, 2),(411, 410, 1),(410, 405, 2),(410, 406, 1),(410, 407, 1),(410, 408, 1),(410, 409, 2),(410, 411, 2),(409, 405, 1),(409, 407, 1),(409, 410, 1),(409, 411, 1),(405, 407, 2),(405, 409, 2),(405, 411, 2)])
#G.add_weighted_edges_from([(411, 405, 2),(411, 406, 0),(411, 407, 2),(411, 408, 0),(411, 409, 2),(411, 410, 1),(410, 405, 2),(410, 406, 1),(410, 407, 1),(410, 408, 1),(410, 409, 2),(410, 411, 2),(409, 405, 1),(409, 407, 1),(409, 410, 1),(409, 411, 1),(405, 407, 2),(405, 409, 2),(405, 411, 2)])


partition = [frozenset([405,
407,
409,
411])
,frozenset([406,408,410])]
Q = mymodularity(G,partition)
print(Q)