# apps/api/src/routers/v1/graph.py
"""Router for Fraud Network Graph Intelligence and Syndicate Cluster Discovery."""

import asyncio
from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from apps.api.src.core.security import verify_api_key
from apps.api.src.schemas.graph_schema import (
    NodesResponse,
    CentralityResponse,
    ClustersResponse,
    GraphDataResponse,
)
from apps.api.src.services.graph_service import graph_service

router = APIRouter(
    prefix="/graph",
    tags=["Fraud Syndicate Graph Intelligence"],
    dependencies=[Depends(verify_api_key)],
)


@router.get("/nodes", response_model=NodesResponse, status_code=status.HTTP_200_OK)
async def get_graph_nodes(
    entity_type: Optional[str] = Query(
        None,
        description="Filter nodes by entity type: Victim, Phone, UPI, BankAccount, Transaction, Incident",
    ),
    incident_id: Optional[str] = Query(
        None,
        description="Filter graph to nodes associated with a specific incident ID",
    ),
    limit: int = Query(
        1000,
        ge=1,
        le=10000,
        description="Maximum number of nodes to return",
    ),
):
    """
    Returns fraud network nodes and connecting links matching optional filters.
    If no data has been registered, returns an empty dataset without synthetic fabrication.
    """
    result = await asyncio.to_thread(
        graph_service.get_nodes,
        entity_type=entity_type,
        incident_id=incident_id,
        limit=limit,
    )
    return result


@router.get("/centrality", response_model=CentralityResponse, status_code=status.HTTP_200_OK)
async def get_graph_centrality(
    top_n: int = Query(15, ge=1, le=100, description="Number of top influential hub entities to rank"),
):
    """
    Returns PageRank and Betweenness Centrality metrics for all entities in the graph.
    Identifies high-traffic scam call hubs and mule bank account bridges.
    """
    result = await asyncio.to_thread(graph_service.get_centrality, top_n=top_n)
    return result


@router.get("/clusters", response_model=ClustersResponse, status_code=status.HTTP_200_OK)
async def get_graph_clusters():
    """
    Returns detected syndicate rings and suspect clusters using Louvain community detection.
    """
    clusters = await asyncio.to_thread(graph_service.get_syndicate_clusters)
    return {
        "clusters": clusters,
        "total_clusters": len(clusters),
    }


@router.get("", response_model=GraphDataResponse, status_code=status.HTTP_200_OK)
@router.get("/data", response_model=GraphDataResponse, status_code=status.HTTP_200_OK)
async def get_full_fraud_graph():
    """
    Returns the consolidated multi-entity fraud connection graph with nodes, links, and centrality.
    """
    result = await asyncio.to_thread(graph_service.get_graph_data)
    return result
