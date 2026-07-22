import json
import networkx as nx
import os

def build_graph_from_file(file_path):
    """
    Reads fraud reports from a JSON file and constructs an undirected NetworkX Graph.
    
    Nodes represent entities:
    - Victim (prefixed 'victim:')
    - Phone (prefixed 'phone:')
    - UPI ID (prefixed 'upi:')
    - Bank Account (prefixed 'bank:')
    - Device Fingerprint (prefixed 'device:')
    
    Edges connect Victim nodes to their reported identifiers.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    with open(file_path, 'r') as f:
        reports = json.load(f)
        
    G = nx.Graph()
    
    for report in reports:
        victim_id = report.get('victimId')
        victim_name = report.get('victimName')
        phone = report.get('phoneNumber')
        upi = report.get('upiId')
        bank = report.get('bankAccount')
        device = report.get('deviceFingerprint')
        
        if not victim_id:
            continue
            
        # Create Victim Node
        vic_node = f"victim:{victim_id}"
        G.add_node(
            vic_node,
            type="Victim",
            label=victim_name,
            victimId=victim_id
        )
        
        # Link Phone Node if present
        if phone and phone.strip():
            phone_node = f"phone:{phone.strip()}"
            G.add_node(phone_node, type="Phone", label=phone)
            G.add_edge(vic_node, phone_node)
            
        # Link UPI Node if present
        if upi and upi.strip():
            upi_node = f"upi:{upi.strip()}"
            G.add_node(upi_node, type="UPI", label=upi)
            G.add_edge(vic_node, upi_node)
            
        # Link Bank Account Node if present
        if bank and bank.strip():
            bank_node = f"bank:{bank.strip()}"
            G.add_node(bank_node, type="BankAccount", label=bank)
            G.add_edge(vic_node, bank_node)
            
        # Link Device Node if present
        if device and device.strip():
            device_node = f"device:{device.strip()}"
            G.add_node(device_node, type="Device", label=device)
            G.add_edge(vic_node, device_node)
            
    return G

if __name__ == "__main__":
    # Test building the graph from the synthetic data
    dir_path = os.path.dirname(__file__)
    json_path = os.path.join(dir_path, "synthetic_reports.json")
    try:
        graph = build_graph_from_file(json_path)
        print(f"Successfully built graph!")
        print(f"Total Nodes: {graph.number_of_nodes()}")
        print(f"Total Edges: {graph.number_of_edges()}")
    except Exception as e:
        print(f"Failed to build graph: {e}")
