import argparse
import os
import sys # For sys.exit

# Local module imports
from ospf_parser import parse_ospf_data
from ospf_graph_builder import create_network_graph
from ospf_visualizer_core import visualize_network_graph

def main():
    """
    Main function to drive the OSPF visualization tool.
    Parses command-line arguments, reads OSPF data, builds a graph,
    and generates a visualization.
    """
    parser = argparse.ArgumentParser(
        description="Visualize OSPF network topology from OSPF command output."
    )
    parser.add_argument(
        "input_file",
        help="Path to the text file containing OSPF data (e.g., 'show ip ospf database' output)."
    )
    parser.add_argument(
        "-o", "--output",
        default="ospf_topology.png",
        help="Output filename for the generated topology image. Default: ospf_topology.png"
    )

    args = parser.parse_args()

    # --- File Handling and Error Checking ---
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' not found.", file=sys.stderr)
        sys.exit(1)
    
    if not os.path.isfile(args.input_file):
        print(f"Error: Input path '{args.input_file}' is not a file.", file=sys.stderr)
        sys.exit(1)

    try:
        # --- Processing Pipeline ---
        print(f"Reading OSPF data from '{args.input_file}'...")
        with open(args.input_file, 'r') as f:
            ospf_data_string = f.read()

        if not ospf_data_string.strip():
            print("Error: Input file is empty.", file=sys.stderr)
            sys.exit(1)

        print("Parsing OSPF data...")
        nodes, edges = parse_ospf_data(ospf_data_string)

        if not nodes:
            print("No OSPF router data found or parsed from the input file. Cannot generate visualization.", file=sys.stderr)
            sys.exit(1)
        
        print(f"Found {len(nodes)} nodes and {len(edges)} edges.")

        print("Creating network graph...")
        network_graph = create_network_graph(nodes, edges)

        if network_graph is None: # Should not happen if create_network_graph is robust
            print("Error: Failed to create network graph.", file=sys.stderr)
            sys.exit(1)

        print(f"Generating visualization and saving to '{args.output}'...")
        visualize_network_graph(network_graph, args.output)
        # Confirmation is typically printed by visualize_network_graph itself.
        # If not, add: print(f"Network topology visualization saved to {args.output}")

    except FileNotFoundError: # Should be caught by os.path.exists, but as a safeguard
        print(f"Error: Input file '{args.input_file}' disappeared during processing.", file=sys.stderr)
        sys.exit(1)
    except ImportError as e:
        print(f"Error: A required module could not be imported: {e}", file=sys.stderr)
        print("Please ensure all dependencies (networkx, matplotlib) and local modules are correctly installed and accessible.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        # For debugging, you might want to print the full traceback
        # import traceback
        # traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
