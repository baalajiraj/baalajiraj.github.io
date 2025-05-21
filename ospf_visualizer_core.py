import networkx as nx
import matplotlib.pyplot as plt

def visualize_network_graph(graph, output_filename="ospf_topology.png"):
    """
    Generates a visualization of a network graph and saves it to a file.

    Args:
        graph (networkx.Graph): The graph object to visualize.
        output_filename (str): The name of the file to save the image to.
                               Defaults to "ospf_topology.png".
    """
    if not isinstance(graph, nx.Graph):
        print("Error: Input is not a valid networkx.Graph object.")
        return

    if graph.number_of_nodes() == 0:
        print("Info: Graph is empty. Generating an empty plot.")

    plt.figure(figsize=(10, 8)) # Adjust figure size for better layout

    # Generate layout
    # Using a seed for reproducibility of the layout
    pos = nx.spring_layout(graph, seed=42, k=0.9) 

    # Draw the graph
    nx.draw(
        graph, 
        pos, 
        with_labels=True, 
        node_size=700, 
        node_color="skyblue", 
        font_size=10, 
        font_weight="bold",
        width=1.5, # Edge thickness
        edge_color="gray"
    )

    # Set title
    plt.title("OSPF Network Topology")

    # Save the plot
    try:
        plt.savefig(output_filename)
        print(f"Graph visualization saved to {output_filename}")
    except Exception as e:
        print(f"Error saving graph visualization: {e}")
    finally:
        # Clear the plot
        plt.clf()
        plt.close() # Close the figure to free memory

if __name__ == '__main__':
    # Example Usage and Basic Test
    print("Running basic test for visualize_network_graph...")

    # 1. Create a sample graph
    sample_g = nx.Graph()
    sample_nodes_list = ['1.1.1.1', '2.2.2.2', '3.3.3.3', '4.4.4.4', '5.5.5.5']
    sample_edges_list = [
        ('1.1.1.1', '2.2.2.2'), 
        ('1.1.1.1', '3.3.3.3'), 
        ('2.2.2.2', '4.4.4.4'),
        ('3.3.3.3', '4.4.4.4'),
        ('4.4.4.4', '5.5.5.5')
    ]
    sample_g.add_nodes_from(sample_nodes_list)
    sample_g.add_edges_from(sample_edges_list)

    # Define an output filename for the test
    test_output_filename = "test_ospf_topology.png"

    # 2. Visualize the graph
    visualize_network_graph(sample_g, test_output_filename)
    
    # (In a real test environment, you might check if the file was created,
    # but for this context, printing the success message is sufficient)
    print(f"Test visualization should be saved as {test_output_filename}")

    # Test with an empty graph
    print("\nTesting with an empty graph...")
    empty_g = nx.Graph()
    visualize_network_graph(empty_g, "empty_topology.png")
    
    # Test with a single node graph
    print("\nTesting with a single node graph...")
    single_node_g = nx.Graph()
    single_node_g.add_node("10.0.0.1")
    visualize_network_graph(single_node_g, "single_node_topology.png")

    print("\nospf_visualizer_core.py executed with basic tests.")
