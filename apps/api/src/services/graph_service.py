# apps/api/src/services/graph_service.py
"""Service layer for Fraud Network Graph Intelligence and Syndicate Cluster Discovery."""

from typing import Any, Dict, List, Optional
from rakshagrid.common.logging.logger import setup_logger
from rakshagrid.ai_graph.service import GraphEngineService, graph_engine_service

logger = setup_logger("rakshagrid.api.graph")


class GraphService:
    """Orchestrates graph intelligence operations, delegation to GraphEngineService, and report registry."""

    def __init__(self, engine: Optional[GraphEngineService] = None):
        self._engine = engine or graph_engine_service

    def get_reports(self) -> List[Dict[str, Any]]:
        """Returns all ingested fraud crime reports."""
        return self._engine.get_reports()

    def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Returns a specific incident report by ID."""
        return self._engine.get_report(report_id)

    def add_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Appends a new citizen crime report to the active graph registry."""
        return self._engine.add_report(report_data)

    def get_nodes(
        self,
        entity_type: Optional[str] = None,
        incident_id: Optional[str] = None,
        limit: int = 1000,
    ) -> Dict[str, Any]:
        """Returns filtered graph nodes and edges."""
        return self._engine.get_nodes(
            entity_type=entity_type,
            incident_id=incident_id,
            limit=limit,
        )

    def get_centrality(self, top_n: int = 15) -> Dict[str, Any]:
        """Returns PageRank and Betweenness centrality metrics."""
        return self._engine.get_centrality(top_n=top_n)

    def get_syndicate_clusters(self) -> List[Dict[str, Any]]:
        """Returns detected community clusters and suspect syndicates."""
        return self._engine.get_clusters()

    def get_graph_data(self) -> Dict[str, Any]:
        """Constructs and analyzes the consolidated fraud network graph."""
        return self._engine.get_full_graph_data()

    def clear(self):
        """Clears all registered reports and graph caches."""
        self._engine.clear()

    def load_demo_data(self, fixture_path: Optional[str] = None):
        """Loads demo synthetic records when explicitly called for development or testing."""
        self._engine.load_demo_data(fixture_path=fixture_path)


graph_service = GraphService()
