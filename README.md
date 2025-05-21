# OSPF Network Topology Visualizer

This script parses Cisco OSPF database output to generate a visual representation of the network topology.

## Description

The `ospf_visualizer.py` script takes a text file containing the output of a Cisco `show ip ospf database` command (or similarly formatted data), parses it to identify routers and their connections, and then uses `networkx` and `matplotlib` to create and save an image of the network graph.

## Input File Format

The script expects an input file that includes "Router Link States" and "Net Link States" sections, similar to the provided `sample_ospf_data.txt`. Key information extracted includes:
*   Router IDs
*   Point-to-point links between routers
*   Connections to transit networks and the routers attached to them.

Refer to `sample_ospf_data.txt` for a concrete example.

## Requirements

*   Python 3.x
*   `networkx`
*   `matplotlib`

You can install the required libraries using pip:
```bash
pip install networkx matplotlib
```

## Usage

To run the script, execute the following command in your terminal:

```bash
python ospf_visualizer.py <path_to_ospf_data_file> [options]
```

**Arguments:**
*   `<path_to_ospf_data_file>`: (Required) The path to the text file containing the OSPF database output.
*   `--output <filename>` or `-o <filename>`: (Optional) The name of the output image file. Defaults to `ospf_topology.png`.

**Example:**

```bash
python ospf_visualizer.py sample_ospf_data.txt -o my_network.png
```
This command will process `sample_ospf_data.txt` and save the network topology visualization as `my_network.png`.
