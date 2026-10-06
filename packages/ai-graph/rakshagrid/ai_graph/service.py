# packages/ai-graph/rakshagrid/ai_graph/service.py
"""
Service layer for Fraud Network Graph Intelligence.

Manages dynamic graph updates, caching, centrality computation, community detection,
and query filtering. Ensures clean empty-state handling without hardcoded data.
"""

import os
import uuid
import networkx as nx
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from rakshagrid.common.exceptions.base import ValidationException
from rakshagrid.common.logging.logger import setup_logger
from rakshagrid.common.utils.json_utils import load_json
from rakshagrid.ai_graph.models.entity import EntityType
from rakshagrid.ai_graph.builder.graph_builder import GraphBuilder
from rakshagrid.ai_graph.analytics.centrality import compute_centrality_metrics
from rakshagrid.ai_graph.analytics.communities import detect_communities

logger = setup_logger("rakshagrid.ai_graph.service")


class GraphEngineService:
    """Core stateful graph engine providing cached analytics and sub-graph filtering."""

    def __init__(self, load_seed_data: bool = False):
        self._reports: List[Dict[str, Any]] = []
        self._dirty: bool = True
        self._cached_graph: Optional[nx.Graph] = None
        self._cached_centrality: Optional[Dict[str, Any]] = None
        self._cached_clusters: Optional[List[Dict[str, Any]]] = None

        if load_seed_data:
            self.load_demo_data()

    def clear(self):
        """Empties graph repository and invalidates cache."""
        self._reports = []
        self._invalidate_cache()

    def _invalidate_cache(self):
        """Marks cached computations dirty."""
        self._dirty = True
        self._cached_graph = None
        self._cached_centrality = None
        self._cached_clusters = None

    def add_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Registers an incident report, invalidates graph cache, and returns the persisted record.
        """
        report_id = report_data.get("id") or f"REP-{uuid.uuid4().hex[:6].upper()}"
        victim_id = report_data.get("victimId") or f"VIC-{uuid.uuid4().hex[:6].upper()}"

        record = {
            "id": report_id,
            "victimId": victim_id,
            "victimName": report_data.get("victimName", "Anonymous Citizen"),
            "phoneNumber": report_data.get("phoneNumber", ""),
            "upiId": report_data.get("upiId", ""),
            "bankAccount": report_data.get("bankAccount", ""),
            "deviceFingerprint": report_data.get("deviceFingerprint", ""),
            "typeOfScam": report_data.get("typeOfScam", "Cyber Fraud"),
            "description": report_data.get("description", ""),
            "amountLost": float(report_data.get("amountLost", 0.0)),
            "city": report_data.get("city", ""),
            "state": report_data.get("state", ""),
            "timestamp": report_data.get("timestamp") or datetime.now(timezone.utc).isoformat(),
            "riskScore": float(report_data.get("riskScore", 0.5)),
            "riskBand": report_data.get("riskBand", "needs_review"),
        }

        self._reports.append(record)
        self._invalidate_cache()
        logger.info(f"Added incident report {report_id}. Total registered reports: {len(self._reports)}")
        return record

    def get_reports(self) -> List[Dict[str, Any]]:
        """Returns all ingested incident reports."""
        return self._reports

    def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Returns a specific report by id or None if not found."""
        for r in self._reports:
            if r.get("id") == report_id:
                return r
        return None

    def _ensure_graph(self) -> nx.Graph:
        """Constructs graph if dirty, otherwise returns cached graph instance."""
        if self._dirty or self._cached_graph is None:
            self._cached_graph = GraphBuilder.build_graph(self._reports)
            self._dirty = False
            # Clear dependent analytic caches
            self._cached_centrality = None
            self._cached_clusters = None
        return self._cached_graph

    def get_nodes(
        self,
        entity_type: Optional[str] = None,
        incident_id: Optional[str] = None,
        limit: int = 1000,
    ) -> Dict[str, Any]:
        """
        Retrieves graph nodes and active links matching optional query filters.
        Validates entity_type against known schema.
        """
        if limit < 1:
            raise ValidationException("Query parameter 'limit' must be greater than or equal to 1.")

        if entity_type:
            clean_type = entity_type.strip()
            if not EntityType.has_value(clean_type):
                allowed = [e.value for e in EntityType]
                raise ValidationException(
                    f"Invalid entity_type '{entity_type}'. Allowed types: {', '.join(allowed)}"
                )
            target_type = EntityType.from_str(clean_type).value
        else:
            target_type = None

        G = self._ensure_graph()
        if len(G) == 0:
            return {"nodes": [], "links": [], "total_nodes": 0, "total_links": 0}

        # Subgraph filtering by incident_id
        if incident_id:
            clean_inc = incident_id.strip()
            inc_node_name = f"incident:{clean_inc}"
            if inc_node_name in G:
                # Include incident node and all connected neighbors
                valid_nodes = {inc_node_name} | set(G.neighbors(inc_node_name))
            else:
                # Incident not present in graph
                valid_nodes = set()
        else:
            valid_nodes = set(G.nodes())

        # Filter by entity_type
        if target_type:
            valid_nodes = {
                n for n in valid_nodes if G.nodes[n].get("type") == target_type
            }

        # Apply limit to nodes
        selected_nodes = sorted(list(valid_nodes))[:limit]
        selected_set = set(selected_nodes)

        nodes_list = []
        for n in selected_nodes:
            data = G.nodes[n]
            nodes_list.append({
                "id": str(n),
                "type": data.get("type", "Unknown"),
                "label": str(data.get("label", n)),
                "properties": {k: v for k, v in data.items() if k not in ["type", "label"]},
            })

        links_list = []
        for u, v, data in G.edges(data=True):
            if u in selected_set and v in selected_set:
                links_list.append({
                    "source": str(u),
                    "target": str(v),
                    "relation": data.get("relation", "connected"),
                    "weight": float(data.get("weight", 1.0)),
                })

        return {
            "nodes": nodes_list,
            "links": links_list,
            "total_nodes": len(nodes_list),
            "total_links": len(links_list),
        }

    def get_centrality(self, top_n: int = 15) -> Dict[str, Any]:
        """Returns PageRank and Betweenness Centrality metrics (cached)."""
        G = self._ensure_graph()
        if len(G) == 0:
            return {"pagerank": {}, "betweenness": {}, "top_influencers": []}

        if self._cached_centrality is None:
            self._cached_centrality = compute_centrality_metrics(G, top_n=top_n)

        return self._cached_centrality

    def get_clusters(self) -> List[Dict[str, Any]]:
        """Returns detected syndicate clusters using Louvain community detection (cached)."""
        G = self._ensure_graph()
        if len(G) == 0:
            return []

        if self._cached_clusters is None:
            self._cached_clusters = detect_communities(G)

        return self._cached_clusters

    def get_full_graph_data(self) -> Dict[str, Any]:
        """Provides consolidated graph data payload for visualization views."""
        nodes_res = self.get_nodes(limit=10000)
        centrality = self.get_centrality()
        clusters = self.get_clusters()

        # Compute hub confidence scores
        confidence_scores = {}
        G = self._ensure_graph()
        for node, data in G.nodes(data=True):
            if data.get("type") in ["Phone", "UPI", "BankAccount"]:
                deg = G.degree(node)
                if deg > 1:
                    confidence_scores[str(node)] = round(1.0 - (1.0 / deg), 3)

        return {
            "nodes": nodes_res["nodes"],
            "links": nodes_res["links"],
            "centrality": {
                "pagerank": centrality.get("pagerank", {}),
                "betweenness": centrality.get("betweenness", {}),
            },
            "confidence_scores": confidence_scores,
            "syndicates_detected": len(clusters),
        }

    def load_demo_data(self, fixture_path: Optional[str] = None):
        """Explicitly loads synthetic demo records for testing/demonstration."""
        if not fixture_path:
            dir_path = os.path.dirname(__file__)
            fixture_path = os.path.join(dir_path, "synthetic_reports.json")

        if os.path.exists(fixture_path):
            records = load_json(fixture_path)
            if isinstance(records, list):
                self._reports = records
                self._invalidate_cache()
                logger.info(f"Loaded {len(records)} demo reports into GraphEngineService.")


# Global service instance with clean empty default state
graph_engine_service = GraphEngineService(load_seed_data=False)
