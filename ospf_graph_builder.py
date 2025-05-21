import networkx as nx

def create_network_graph(nodes, edges):
    """
    Creates a networkx.Graph object from a list of nodes and edges.

    Args:
        nodes (list or set): A list or set of node identifiers (e.g., router IDs as strings).
        edges (list): A list of tuples, where each tuple represents an edge 
                      between two nodes (e.g., ('1.1.1.1', '2.2.2.2')).

    Returns:
        networkx.Graph: A populated networkx.Graph object.
    """
    G = nx.Graph()
    
    if nodes:
        G.add_nodes_from(nodes)
    
    if edges:
        G.add_edges_from(edges)
        
    return G

if __name__ == '__main__':
    # Example Usage and Basic Test
    sample_nodes = ['1.1.1.1', '2.2.2.2', '3.3.3.3', '4.4.4.4']
    sample_edges = [
        ('1.1.1.1', '2.2.2.2'), 
        ('1.1.1.1', '3.3.3.3'), 
        ('2.2.2.2', '4.4.4.4')
    ]

    # Create the graph
    network_graph = create_network_graph(sample_nodes, sample_edges)

    # Basic Verification
    print("Nodes in graph:", list(network_graph.nodes()))
    print("Edges in graph:", list(network_graph.edges()))
    print("Number of nodes:", network_graph.number_of_nodes())
    print("Number of edges:", network_graph.number_of_edges())

    assert set(network_graph.nodes()) == set(sample_nodes), "Node set mismatch"
    # For edges, NetworkX might store them in a different order within the tuple,
    # so we need to normalize them for comparison if that's a concern.
    # However, add_edges_from and G.edges() typically maintain specified order for undirected.
    # A more robust check for edges:
    expected_edge_set = {tuple(sorted(edge)) for edge in sample_edges}
    actual_edge_set = {tuple(sorted(edge)) for edge in network_graph.edges()}
    assert actual_edge_set == expected_edge_set, "Edge set mismatch"

    print("\nGraph created successfully with the following properties:")
    print(f"Nodes: {network_graph.nodes()}")
    print(f"Edges: {network_graph.edges()}")

    # Test with empty nodes and edges
    empty_graph = create_network_graph([], [])
    print("\nEmpty graph test:")
    print(f"Nodes: {empty_graph.nodes()}")
    print(f"Edges: {empty_graph.edges()}")
    assert empty_graph.number_of_nodes() == 0
    assert empty_graph.number_of_edges() == 0
    
    print("\nospf_graph_builder.py executed successfully with basic tests passing.")
