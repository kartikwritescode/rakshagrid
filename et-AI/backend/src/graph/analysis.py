import json
import networkx as nx
import os
import sys
import argparse
from graph_builder import build_graph_from_file

def export_pyvis_graph(G, out_path, pagerank_scores, betweenness_scores, confidence_scores):
    """
    Constructs an interactive PyVis Network visualization of the fraud graph.
    Configures node colors, size, tooltips (HTML metadata), and vis.js physics.
    Saves the output to out_path.
    """
    try:
        from pyvis.network import Network
    except ImportError:
        print("Warning: pyvis not installed. Skipping HTML export.", file=sys.stderr)
        return

    # Theme colors matching Tailwind dark design
    colors = {
        "Victim": "#6366f1",      # Indigo
        "Phone": "#f97316",       # Orange
        "UPI": "#eab308",         # Yellow
        "BankAccount": "#10b981",  # Emerald
        "Device": "#f43f5e"       # Rose
    }

    # Initialize PyVis network (bgcolor matching Slate-950)
    net = Network(height="100%", width="100%", bgcolor="#020617", font_color="#e2e8f0", heading="")

    # Add nodes to PyVis with customized styles
    for node, data in G.nodes(data=True):
        node_type = data.get('type', 'Unknown')
        label = data.get('label', node)
        color = colors.get(node_type, "#94a3b8")
        
        degree = G.degree(node)
        pr = pagerank_scores.get(node, 0.0)
        bc = betweenness_scores.get(node, 0.0)
        conf = confidence_scores.get(node, None)
        
        # Tooltip HTML
        tooltip = f"""
        <div style="font-family: 'Outfit', sans-serif; padding: 12px; border-radius: 8px; background-color: #0f172a; color: #f1f5f9; border: 1px solid #334155; font-size: 11px; line-height: 1.5; min-width: 190px;">
          <b style="color: {color}; font-size: 13px; text-transform: uppercase;">{node_type} Entity</b><br/>
          <span style="font-weight: 600; font-size: 12px; color: #ffffff; word-break: break-all;">{label}</span><br/>
          <hr style="border: 0; border-top: 1px solid #334155; margin: 8px 0;"/>
          <b>Connections:</b> {degree}<br/>
          <b>PageRank Score:</b> {pr:.5f}<br/>
          <b>Betweenness Score:</b> {bc:.5f}<br/>
        """
        if conf is not None:
            tooltip += f"<b>Fraud Risk:</b> <span style='color: #f43f5e; font-weight: bold;'>{(conf * 100):.0f}%</span><br/>"
        
        tooltip += "</div>"

        # Victims are smaller circles; shared hubs are larger hexagons
        size = 14 if node_type == "Victim" else 22
        shape = "dot" if node_type == "Victim" else "hexagon"

        net.add_node(
            node,
            label=label,
            title=tooltip,
            color=color,
            size=size,
            shape=shape,
            borderWidth=2,
            borderWidthSelected=4.5
        )

    # Add edges
    for source, target in G.edges():
        net.add_edge(source, target, color="rgba(99, 102, 241, 0.2)", width=1.5)

    # Physics config, navigation overlays, hover-highlighters
    options = """
    var options = {
      "nodes": {
        "font": {
          "size": 11,
          "face": "Outfit, sans-serif"
        }
      },
      "edges": {
        "color": {
          "inherit": false
        },
        "smooth": {
          "enabled": false
        }
      },
      "interaction": {
        "hover": true,
        "tooltipDelay": 150,
        "hideEdgesOnDrag": false,
        "hideEdgesOnZoom": false,
        "navigationButtons": true
      },
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -12000,
          "centralGravity": 0.35,
          "springLength": 95,
          "springConstant": 0.04,
          "damping": 0.9
        },
        "minVelocity": 0.75,
        "stabilization": {
          "enabled": true,
          "iterations": 200,
          "updateInterval": 25
        }
      }
    }
    """
    net.set_options(options)
    
    # Save graph HTML
    net.save_graph(out_path)
    print(f"Generated PyVis visualization graph HTML at: {out_path}", file=sys.stderr)


def analyze_fraud_graph(G):
    """
    Analyzes the constructed fraud connection graph G and returns metrics.
    """
    if len(G) == 0:
        return {
            "communities": [],
            "centrality": {
                "pagerank": {},
                "betweenness": {}
            },
            "graph stats": {
                "totalNodes": 0,
                "totalEdges": 0,
                "density": 0.0,
                "numberConnectedComponents": 0,
                "nodeTypeCounts": {}
            },
            "confidence scores": {}
        }
    
    # Louvain Community Detection
    try:
        communities_sets = nx.community.louvain_communities(G, seed=42)
        communities = []
        for idx, com_set in enumerate(communities_sets):
            communities.append({
                "id": idx,
                "nodes": sorted(list(com_set))
            })
    except Exception:
        communities = [{
            "id": idx,
            "nodes": sorted(list(c))
        } for idx, c in enumerate(nx.connected_components(G))]

    # PageRank
    pagerank_scores = nx.pagerank(G)
    
    # Betweenness Centrality
    betweenness_scores = nx.betweenness_centrality(G)
    
    # Degrees
    degrees = dict(G.degree())
    
    # Confidence Risk Scores (Shared hubs)
    confidence_scores = {}
    for node, data in G.nodes(data=True):
        node_type = data.get('type')
        if node_type == "Victim":
            continue
            
        deg = degrees.get(node, 0)
        if deg > 1:
            confidence = 1.0 - (1.0 / deg)
            confidence_scores[node] = round(confidence, 3)

    # General Stats
    node_types = nx.get_node_attributes(G, 'type')
    node_type_counts = {}
    for t in node_types.values():
        node_type_counts[t] = node_type_counts.get(t, 0) + 1
        
    num_components = nx.number_connected_components(G)
    density = nx.density(G)
    
    graph_stats = {
        "totalNodes": G.number_of_nodes(),
        "totalEdges": G.number_of_edges(),
        "density": density,
        "numberConnectedComponents": num_components,
        "nodeTypeCounts": node_type_counts
    }
    
    return {
        "communities": communities,
        "centrality": {
            "pagerank": pagerank_scores,
            "betweenness": betweenness_scores
        },
        "graph stats": graph_stats,
        "confidence scores": confidence_scores
    }

def main():
    parser = argparse.ArgumentParser(description="Analyze fraud report network graph.")
    parser.add_argument(
        "--file", 
        type=str, 
        help="Path to the reports JSON file",
        default=os.path.join(os.path.dirname(__file__), "synthetic_reports.json")
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Path to write analysis output JSON file (optional)"
    )
    parser.add_argument(
        "--html_out",
        type=str,
        help="Path to write PyVis HTML visualization (optional)"
    )
    
    args = parser.parse_args()
    
    try:
        # Build network graph
        G = build_graph_from_file(args.file)
        
        # Analyze metrics
        results = analyze_fraud_graph(G)
        
        # Run PyVis visualization export if requested
        if args.html_out:
            export_pyvis_graph(
                G, 
                args.html_out, 
                results["centrality"]["pagerank"], 
                results["centrality"]["betweenness"], 
                results["confidence scores"]
            )
            
        json_output = json.dumps(results, indent=2)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(json_output)
            print(f"Analysis written to: {args.output}")
        else:
            # Print analysis JSON output to stdout for child_process capture
            print(json_output)
            
    except Exception as e:
        print(f"Error executing analysis: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
