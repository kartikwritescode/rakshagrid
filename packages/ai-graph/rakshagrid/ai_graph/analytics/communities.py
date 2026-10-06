# packages/ai-graph/rakshagrid/ai_graph/analytics/communities.py
"""Community detection module using Louvain algorithm and connected components fallback."""

import networkx as nx
from typing import Any, Dict, List
from rakshagrid.common.logging.logger import setup_logger

logger = setup_logger("rakshagrid.ai_graph.communities")


def detect_communities(G: nx.Graph) -> List[Dict[str, Any]]:
    """
    Detects syndicate clusters and fraud communities in graph G.
    Uses NetworkX Louvain modularity optimization with connected-components fallback.
    Calculates per-cluster risk score based on multi-victim shared payment/contact hubs.
    """
    if len(G) == 0:
        return []

    try:
        # Louvain Community Detection (deterministic seed)
        community_sets = nx.community.louvain_communities(G, seed=42)
    except Exception as e:
        logger.debug(f"Louvain clustering fallback to connected components: {e}")
        community_sets = list(nx.connected_components(G))

    clusters: List[Dict[str, Any]] = []

    for idx, com_nodes in enumerate(community_sets):
        sorted_nodes = sorted([str(n) for n in com_nodes])
        entity_counts: Dict[str, int] = {}
        victim_count = 0
        shared_hub_count = 0

        for node_id in sorted_nodes:
            node_data = G.nodes[node_id] if node_id in G else {}
            ent_type = node_data.get("type", "Unknown")
            entity_counts[ent_type] = entity_counts.get(ent_type, 0) + 1

            if ent_type == "Victim":
                victim_count += 1
            elif ent_type in ["Phone", "UPI", "BankAccount"]:
                # Check degree: if linked to multiple victims, it's a shared scam hub
                deg = G.degree(node_id) if node_id in G else 0
                if deg > 1:
                    shared_hub_count += 1

        # Calculate cluster risk score: high if multiple victims share phone/UPI/bank hubs
        if victim_count > 1 and shared_hub_count > 0:
            risk_score = round(min(0.5 + 0.15 * shared_hub_count + 0.1 * victim_count, 0.99), 3)
        elif shared_hub_count > 0:
            risk_score = round(min(0.4 + 0.1 * shared_hub_count, 0.85), 3)
        else:
            risk_score = 0.25

        clusters.append({
            "id": idx,
            "nodes": sorted_nodes,
            "size": len(sorted_nodes),
            "entity_counts": entity_counts,
            "risk_score": risk_score,
        })

    # Sort descending by risk score and size
    clusters.sort(key=lambda c: (c["risk_score"], c["size"]), reverse=True)
    return clusters
