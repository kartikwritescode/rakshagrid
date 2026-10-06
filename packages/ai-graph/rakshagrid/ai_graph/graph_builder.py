import json
import networkx as nx
import os

def build_graph_from_reports(reports: list) -> nx.Graph:
    """
    Constructs an undirected NetworkX Graph from a list of fraud report dicts.
    
    Nodes represent entities:
    - Victim (prefixed 'victim:')
    - Phone (prefixed 'phone:')
    - UPI ID (prefixed 'upi:')
    - Bank Account (prefixed 'bank:')
    - Device Fingerprint (prefixed 'device:')
    
    Edges connect Victim nodes to their reported identifiers.
    """
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
        if phone and str(phone).strip():
            phone_node = f"phone:{str(phone).strip()}"
            G.add_node(phone_node, type="Phone", label=str(phone))
            G.add_edge(vic_node, phone_node)
            
        # Link UPI Node if present
        if upi and str(upi).strip():
            upi_node = f"upi:{str(upi).strip()}"
            G.add_node(upi_node, type="UPI", label=str(upi))
            G.add_edge(vic_node, upi_node)
            
        # Link Bank Account Node if present
        if bank and str(bank).strip():
            bank_node = f"bank:{str(bank).strip()}"
            G.add_node(bank_node, type="BankAccount", label=str(bank))
            G.add_edge(vic_node, bank_node)
            
        # Link Device Node if present
        if device and str(device).strip():
            device_node = f"device:{str(device).strip()}"
            G.add_node(device_node, type="Device", label=str(device))
            G.add_edge(vic_node, device_node)
            
    return G

def build_graph_from_file(file_path: str) -> nx.Graph:
    """Reads fraud reports from a JSON file and constructs an undirected NetworkX Graph."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
        
    with open(file_path, 'r', encoding='utf-8') as f:
        reports = json.load(f)
        
    return build_graph_from_reports(reports)

if __name__ == "__main__":
    dir_path = os.path.dirname(__file__)
    json_path = os.path.join(dir_path, "synthetic_reports.json")
    try:
        graph = build_graph_from_file(json_path)
        print(f"Successfully built graph!")
        print(f"Total Nodes: {graph.number_of_nodes()}")
        print(f"Total Edges: {graph.number_of_edges()}")
    except Exception as e:
        print(f"Failed to build graph: {e}")
