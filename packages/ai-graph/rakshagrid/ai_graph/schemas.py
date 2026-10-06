# packages/ai-graph/rakshagrid/ai_graph/schemas.py
"""Typed Pydantic schemas for Fraud Network Graph endpoints and serialization."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class GraphNodeSchema(BaseModel):
    id: str = Field(..., description="Unique node ID")
    type: str = Field(..., description="Entity type: Victim, Phone, UPI, BankAccount, Transaction, Incident")
    label: str = Field(..., description="Entity display label")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Custom node properties")


class GraphLinkSchema(BaseModel):
    source: str = Field(..., description="Source node id")
    target: str = Field(..., description="Target node id")
    relation: str = Field(default="connected", description="Semantic relationship type")
    weight: float = Field(default=1.0, description="Connection strength weight")


class NodesResponse(BaseModel):
    nodes: List[GraphNodeSchema] = Field(default_factory=list, description="List of graph entity nodes")
    links: List[GraphLinkSchema] = Field(default_factory=list, description="List of entity relationship links")
    total_nodes: int = Field(default=0, description="Total nodes returned")
    total_links: int = Field(default=0, description="Total links returned")


class TopInfluencer(BaseModel):
    node_id: str
    type: str
    label: str
    pagerank: float
    betweenness: float
    degree: int


class CentralityResponse(BaseModel):
    pagerank: Dict[str, float] = Field(default_factory=dict, description="PageRank scores by node ID")
    betweenness: Dict[str, float] = Field(default_factory=dict, description="Betweenness centrality scores by node ID")
    top_influencers: List[TopInfluencer] = Field(default_factory=list, description="Top connected hub entities")


class ClusterItem(BaseModel):
    id: int = Field(..., description="Cluster identifier")
    nodes: List[str] = Field(default_factory=list, description="Node IDs belonging to this syndicate cluster")
    size: int = Field(default=0, description="Count of nodes in cluster")
    entity_counts: Dict[str, int] = Field(default_factory=dict, description="Distribution of entity types in cluster")
    risk_score: float = Field(default=0.0, description="Calculated fraud confidence of syndicate cluster")


class ClustersResponse(BaseModel):
    clusters: List[ClusterItem] = Field(default_factory=list, description="List of detected syndicate communities")
    total_clusters: int = Field(default=0, description="Total communities detected")


class GraphDataResponse(BaseModel):
    nodes: List[GraphNodeSchema] = Field(default_factory=list)
    links: List[GraphLinkSchema] = Field(default_factory=list)
    centrality: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    confidence_scores: Dict[str, float] = Field(default_factory=dict)
    syndicates_detected: int = 0
