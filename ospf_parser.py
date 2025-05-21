import re

def parse_ospf_data(ospf_data_str):
    """
    Parses OSPF database information from a string to extract network topology.

    The function identifies routers (nodes) and their connections (edges) 
    based on Router Link States and Net Link States found in the OSPF data.

    Args:
        ospf_data_str (str): A string containing the OSPF database output,
                             similar to 'show ip ospf database' from a Cisco router.

    Returns:
        tuple: A tuple containing two sorted lists:
            - nodes (list): A list of unique router IDs (strings).
            - edges (list): A list of unique connections (tuples of two router IDs, sorted).
                            Example: [('1.1.1.1', '2.2.2.2'), ...]
    """
    nodes = set()
    edges_set = set() # Use a set for edges to automatically handle duplicates

    # Phase 1: Initial Node Discovery (broad phase)
    # Gather all potential router IDs from various parts of the OSPF data.
    # This helps ensure all participating routers are identified early.

    # OSPF Router with ID (X.X.X.X) - typically the router the command was run on.
    ospf_router_id_match = re.search(r"OSPF Router with ID \((\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\)", ospf_data_str)
    if ospf_router_id_match:
        nodes.add(ospf_router_id_match.group(1))

    # ADV Router from LSA lines (e.g., "1.1.1.1      1.1.1.1      ...")
    # The second IP address in such lines is usually the Advertising Router ID.
    adv_router_lsa_matches = re.findall(r"^\s*[\d\.]+\s+(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s+\d+", ospf_data_str, re.MULTILINE)
    for router_id in adv_router_lsa_matches:
        nodes.add(router_id)

    # Neighboring Router ID (from point-to-point links in Router LSAs)
    neighbor_router_matches = re.findall(r"Neighboring Router ID:\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", ospf_data_str)
    for router_id in neighbor_router_matches:
        nodes.add(router_id)

    # Attached Router (from Net LSAs, indicating routers connected to a transit network)
    attached_router_matches = re.findall(r"Attached Router:\s*(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", ospf_data_str)
    for router_id in attached_router_matches:
        nodes.add(router_id)

    # Phase 2: Parse Router Link States for direct router-to-router links
    # Router LSAs describe the state and connections of individual routers.
    router_link_states_section_match = re.search(
        # Regex to find the "Router Link States" section and capture its content.
        # It looks for the section header and captures everything until "Net Link States" or end of string.
        r"Router Link States \(Area \d+\)\s*\n\s*Link ID\s+ADV Router\s+Age\s+Seq#\s+Checksum\s+Link count\s*\n([\s\S]*?)(?=\n\s*Net Link States|\Z)",
        ospf_data_str, re.MULTILINE
    )

    if router_link_states_section_match:
        router_lsa_content_block = router_link_states_section_match.group(1)
        
        # Regex to find each individual Router LSA entry within the captured block.
        # An LSA starts with a non-indented line containing Link ID, ADV Router, etc.,
        # followed by indented lines describing its links.
        router_lsa_entries = re.finditer(
            r"^(?P<lsa_link_id>[\d\.]+)\s+(?P<adv_router>[\d\.]+)\s+\d+\s+0x[\dA-Fa-f]+\s+0x[\dA-Fa-f]+\s+\d+\n" # LSA header line
            r"(?P<links_info>(?:  Link connected to:[^\n]+\n(?:   \(Link ID\)[^\n]+\n(?:   \(Link Data\)[^\n]+\n)?)*)", # Associated link lines (indented)
            router_lsa_content_block,
            re.MULTILINE
        )
        for lsa_entry in router_lsa_entries:
            adv_router_of_lsa = lsa_entry.group("adv_router")
            nodes.add(adv_router_of_lsa) # Ensure ADV router is in nodes
            
            links_info_str = lsa_entry.group("links_info")
            
            # Find point-to-point links within this specific LSA
            ptp_links = re.finditer(
                r"Link connected to: another Router \(point-to-point\)\s*\n\s*\(Link ID\) Neighboring Router ID: (?P<neighbor_id>[\d\.]+)",
                links_info_str
            )
            for ptp_match in ptp_links:
                neighbor_id = ptp_match.group("neighbor_id")
                nodes.add(neighbor_id) # Ensure neighbor is in nodes
                
                # Add edge as a sorted tuple to ensure uniqueness and consistent ordering
                edge = tuple(sorted((adv_router_of_lsa, neighbor_id)))
                edges_set.add(edge)

    # Phase 3: Parse Net Link States for links via transit networks
    # Net LSAs describe transit networks (e.g., Ethernet segments) and the routers connected to them.
    # The ADV Router of a Net LSA is the Designated Router (DR) for that segment.
    net_link_states_section_match = re.search(
        # Regex to find the "Net Link States" section and capture its content.
        # It looks for the section header and captures everything until "Summary Net Link States" or end of string.
        r"Net Link States \(Area \d+\)\s*\n\s*Link ID\s+ADV Router\s+Age\s+Seq#\s+Checksum\s*\n([\s\S]*?)(?=\n\s*Summary Net Link States|\n\s*Type-\d+ AS External Link States|\Z)",
        ospf_data_str, re.MULTILINE
    )

    if net_link_states_section_match:
        net_lsa_content_block = net_link_states_section_match.group(1)

        # Regex to find each individual Net LSA entry within the captured block.
        # A Net LSA starts with its Link ID (DR's interface IP) and ADV Router (DR's Router ID),
        # followed by lines listing attached routers.
        net_lsa_entries = re.finditer(
            r"^(?P<lsa_link_id>[\d\.]+)\s+(?P<adv_router>[\d\.]+)\s+\d+\s+0x[\dA-Fa-f]+\s+0x[\dA-Fa-f]+\n" # Net LSA header line
            r"(?P<attached_routers_info>(?:  Attached Router: [^\n]+\n)*)", # Associated attached router lines (indented)
            net_lsa_content_block,
            re.MULTILINE
        )
        for lsa_entry in net_lsa_entries:
            dr_router_id = lsa_entry.group("adv_router") # ADV Router of Net LSA is the DR
            nodes.add(dr_router_id) # Ensure DR is in nodes
            
            attached_routers_info_str = lsa_entry.group("attached_routers_info")
            
            # Find all routers attached to this transit network
            current_attached_routers = re.findall(r"Attached Router:\s*([\d\.]+)", attached_routers_info_str)
            for attached_router_id in current_attached_routers:
                nodes.add(attached_router_id) # Ensure attached router is in nodes
                if dr_router_id != attached_router_id: # Avoid self-loop for DR
                    # Connect DR to each attached router
                    edge = tuple(sorted((dr_router_id, attached_router_id)))
                    edges_set.add(edge)
    
    return sorted(list(nodes)), sorted(list(edges_set))


if __name__ == '__main__':
    # This section provides a basic test case for the parser.
    # It uses a sample OSPF data string and checks if the parsed nodes and edges
    # match the expected output.
    sample_data = """OSPF Router with ID (1.1.1.1) (Process ID 1)

        Router Link States (Area 0)

Link ID         ADV Router      Age         Seq#       Checksum Link count
1.1.1.1         1.1.1.1         60          0x80000002 0x00ABCD 2
  Link connected to: another Router (point-to-point)
   (Link ID) Neighboring Router ID: 2.2.2.2
   (Link Data) Router Interface address: 10.1.12.1
  Link connected to: a Transit Network
   (Link ID) Designated Router address: 10.1.13.3
   (Link Data) Router Interface address: 10.1.13.1

2.2.2.2         2.2.2.2         65          0x80000003 0x00EFGH 2
  Link connected to: another Router (point-to-point)
   (Link ID) Neighboring Router ID: 1.1.1.1
   (Link Data) Router Interface address: 10.1.12.2
  Link connected to: a Transit Network
   (Link ID) Designated Router address: 10.1.24.4
   (Link Data) Router Interface address: 10.1.24.2

3.3.3.3         3.3.3.3         70          0x80000004 0x00IJKL 1
  Link connected to: a Transit Network
   (Link ID) Designated Router address: 10.1.13.3
   (Link Data) Router Interface address: 10.1.13.3

4.4.4.4         4.4.4.4         75          0x80000005 0x00MNOP 1
  Link connected to: a Transit Network
   (Link ID) Designated Router address: 10.1.24.4
   (Link Data) Router Interface address: 10.1.24.4

        Net Link States (Area 0)

Link ID         ADV Router      Age         Seq#       Checksum
10.1.13.3       3.3.3.3         80          0x80000002 0x00QRST 2
  Attached Router: 3.3.3.3
  Attached Router: 1.1.1.1

10.1.24.4       4.4.4.4         85          0x80000002 0x00UVWX 2
  Attached Router: 4.4.4.4
  Attached Router: 2.2.2.2
"""
    nodes, edges = parse_ospf_data(sample_data)
    print("--- OSPF Parser Test ---")
    print("Parsed Nodes:", nodes)
    print("Parsed Edges:", edges)

    # Expected topology based on the sample_data:
    # Nodes: 1.1.1.1, 2.2.2.2, 3.3.3.3, 4.4.4.4
    # Edges:
    # 1. Point-to-point link between 1.1.1.1 and 2.2.2.2 (from Router LSAs).
    # 2. Transit network 10.1.13.3 (DR is 3.3.3.3) connects 1.1.1.1 and 3.3.3.3 (from Net LSA).
    # 3. Transit network 10.1.24.4 (DR is 4.4.4.4) connects 2.2.2.2 and 4.4.4.4 (from Net LSA).
    expected_nodes = sorted(['1.1.1.1', '2.2.2.2', '3.3.3.3', '4.4.4.4'])
    expected_edges = sorted([
        ('1.1.1.1', '2.2.2.2'), 
        ('1.1.1.1', '3.3.3.3'), 
        ('2.2.2.2', '4.4.4.4')
    ])
    
    assert nodes == expected_nodes, f"Node mismatch during test: Expected {expected_nodes}, Got {nodes}"
    assert edges == expected_edges, f"Edge mismatch during test: Expected {expected_edges}, Got {edges}"
    print("Sample data parsing test successful!")

    # Test with actual file data from sample_ospf_data.txt
    try:
        # Assuming sample_ospf_data.txt is in the same directory for testing.
        # In a real application, this path might need to be handled differently.
        with open('sample_ospf_data.txt', 'r') as f:
            file_data = f.read()
        
        print("\n--- Parsing sample_ospf_data.txt ---")
        nodes_file, edges_file = parse_ospf_data(file_data)
        print("Parsed Nodes from file:", nodes_file)
        print("Parsed Edges from file:", edges_file)
        
        assert nodes_file == expected_nodes, f"Node mismatch from file: Expected {expected_nodes}, Got {nodes_file}"
        assert edges_file == expected_edges, f"Edge mismatch from file: Expected {expected_edges}, Got {edges_file}"
        print("File data parsing test successful!")

    except FileNotFoundError:
        print("\nWarning: sample_ospf_data.txt not found. Skipping file test.")
    except Exception as e:
        print(f"\nError processing file data during test: {e}")
    print("------------------------")
