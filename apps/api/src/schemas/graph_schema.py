# apps/api/src/schemas/graph_schema.py
"""Typed Pydantic schemas for fraud network graph intelligence endpoints."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from rakshagrid.ai_graph.schemas import (
    GraphNodeSchema,
    GraphLinkSchema,
    NodesResponse,
    CentralityResponse,
    TopInfluencer,
    ClusterItem,
    ClustersResponse,
    GraphDataResponse,
)

# Backward-compatibility aliases
GraphNode = GraphNodeSchema
GraphLink = GraphLinkSchema
GraphCentrality = CentralityResponse
GraphResponse = GraphDataResponse

__all__ = [
    "GraphNodeSchema",
    "GraphLinkSchema",
    "NodesResponse",
    "CentralityResponse",
    "TopInfluencer",
    "ClusterItem",
    "ClustersResponse",
    "GraphDataResponse",
    "GraphNode",
    "GraphLink",
    "GraphCentrality",
    "GraphResponse",
]
