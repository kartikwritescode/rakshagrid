# packages/ai-graph/rakshagrid/ai_graph/analytics/centrality.py
"""Centrality analysis module: PageRank, Betweenness Centrality, and Hub Detection."""

import networkx as nx
from typing import Any, Dict, List
from rakshagrid.common.logging.logger import setup_logger

logger = setup_logger("rakshagrid.ai_graph.centrality")


def compute_pagerank(G: nx.Graph, alpha: float = 0.85, max_iter: int = 200) -> Dict[str, float]:
    """Computes PageRank centrality scores for all nodes in graph G."""
    if len(G) == 0:
        return {}
    try:
        raw_scores = nx.pagerank(G, alpha=alpha, max_iter=max_iter)
        return {str(k): round(float(v), 5) for k, v in raw_scores.items()}
    except Exception as e:
        logger.warning(f"PageRank computation fallback: {e}")
        # Uniform fallback for singular or un-converged graphs
        n = len(G)
        return {str(node): round(1.0 / n, 5) for node in G.nodes()}


def compute_betweenness(G: nx.Graph, normalized: bool = True) -> Dict[str, float]:
    """Computes Betweenness Centrality scores for all nodes in graph G."""
    if len(G) == 0:
        return {}
    try:
        raw_scores = nx.betweenness_centrality(G, normalized=normalized)
        return {str(k): round(float(v), 5) for k, v in raw_scores.items()}
    except Exception as e:
        logger.warning(f"Betweenness computation error: {e}")
        return {str(node): 0.0 for node in G.nodes()}


def compute_centrality_metrics(G: nx.Graph, top_n: int = 15) -> Dict[str, Any]:
    """
    Computes PageRank and Betweenness Centrality and ranks top influential hub entities.
    """
    if len(G) == 0:
        return {
            "pagerank": {},
            "betweenness": {},
            "top_influencers": [],
        }

    pr = compute_pagerank(G)
    bc = compute_betweenness(G)
    degrees = dict(G.degree())

    # Build ranked top influencers list
    influencers: List[Dict[str, Any]] = []
    for node, data in G.nodes(data=True):
        n_id = str(node)
        n_type = data.get("type", "Unknown")
        label = data.get("label", n_id)
        influencers.append({
            "node_id": n_id,
            "type": n_type,
            "label": str(label),
            "pagerank": pr.get(n_id, 0.0),
            "betweenness": bc.get(n_id, 0.0),
            "degree": degrees.get(node, 0),
        })

    # Sort descending by composite centrality: PageRank + Betweenness
    influencers.sort(
        key=lambda x: (x["pagerank"] + x["betweenness"], x["degree"]),
        reverse=True,
    )

    return {
        "pagerank": pr,
        "betweenness": bc,
        "top_influencers": influencers[:top_n],
    }
