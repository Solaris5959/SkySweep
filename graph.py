import networkx as nx
import matplotlib.pyplot as plt

"""
Testing graph representation
"""

# Create an empty undirected graph
G = nx.Graph()

# Add nodes
G.add_node(1)
G.add_node(2)
G.add_node(3)
G.add_node(4)

# Add edges (edges are tuples of nodes)
G.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 1)])

# Draw the graph
nx.draw(G, with_labels=True, node_color='lightblue', node_size=500, font_size=12, font_weight='bold', edge_color='gray')

# Show the graph
plt.show()
