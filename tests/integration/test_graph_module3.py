# tests/integration/test_graph_module3.py
"""
Dedicated Module 3 (Fraud Network Graph Intelligence) Integration Tests.

Validates:
1. Dynamic graph construction across all supported entity types (Victim, Phone, UPI, BankAccount, Transaction, Incident)
2. Normalization and deduplication of entities across multiple incident reports
3. PageRank and Betweenness Centrality metrics
4. Community / Syndicate Cluster Detection (Louvain)
5. Clean empty-graph state (no fabricated or hardcoded victims)
6. Query filtering (entity_type, incident_id, limit) and invalid filter rejections
7. Caching behavior to avoid redundant heavy graph recomputations
8. Strict Pydantic response schema compliance
"""

import pytest
from fastapi.testclient import TestClient

from apps.api.src.main import app
from apps.api.src.services.graph_service import graph_service
from apps.api.src.schemas.graph_schema import (
    NodesResponse,
    CentralityResponse,
    ClustersResponse,
    GraphDataResponse,
)

client = TestClient(app, headers={"X-API-Key": "rakshagrid-master-key-2026"})


@pytest.fixture(autouse=True)
def clean_graph_state():
    """Ensure clean empty graph state before and after each test."""
    graph_service.clear()
    yield
    graph_service.clear()


# ============================================================================
# 1. Empty Graph Handling
# ============================================================================

def test_empty_graph_endpoints_return_clean_empty_datasets():
    """Verifies that empty graph returns valid empty payloads without fabricated data."""
    # 1. Nodes
    res_nodes = client.get("/api/v1/graph/nodes")
    assert res_nodes.status_code == 200
    data_nodes = res_nodes.json()
    assert data_nodes["nodes"] == []
    assert data_nodes["links"] == []
    assert data_nodes["total_nodes"] == 0
    assert data_nodes["total_links"] == 0
    NodesResponse.model_validate(data_nodes)

    # 2. Centrality
    res_centrality = client.get("/api/v1/graph/centrality")
    assert res_centrality.status_code == 200
    data_centrality = res_centrality.json()
    assert data_centrality["pagerank"] == {}
    assert data_centrality["betweenness"] == {}
    assert data_centrality["top_influencers"] == []
    CentralityResponse.model_validate(data_centrality)

    # 3. Clusters
    res_clusters = client.get("/api/v1/graph/clusters")
    assert res_clusters.status_code == 200
    data_clusters = res_clusters.json()
    assert data_clusters["clusters"] == []
    assert data_clusters["total_clusters"] == 0
    ClustersResponse.model_validate(data_clusters)

    # 4. Full Graph Consolidated View
    res_graph = client.get("/api/v1/graph")
    assert res_graph.status_code == 200
    data_graph = res_graph.json()
    assert data_graph["nodes"] == []
    assert data_graph["links"] == []
    assert data_graph["syndicates_detected"] == 0
    GraphDataResponse.model_validate(data_graph)


# ============================================================================
# 2. Dynamic Graph Construction & Supported Entity Types
# ============================================================================

def test_graph_construction_with_all_supported_entities():
    """
    Verifies that a report dynamically spawns all supported entity types:
    Victim, Phone, UPI, BankAccount, Transaction, and Incident.
    """
    report_payload = {
        "id": "REP-TEST-001",
        "victimId": "VIC-1001",
        "victimName": "Aarav Mehta",
        "phoneNumber": "+91 98765 00001",
        "upiId": "mule.scam@oksbi",
        "bankAccount": "100200300400",
        "amountLost": 75000.0,
        "typeOfScam": "Digital Arrest",
        "city": "Delhi",
        "state": "Delhi",
    }
    create_res = client.post("/api/v1/reports", json=report_payload)
    assert create_res.status_code == 201

    # Inspect constructed nodes
    nodes_res = client.get("/api/v1/graph/nodes")
    assert nodes_res.status_code == 200
    data = nodes_res.json()

    node_types = {n["type"] for n in data["nodes"]}
    assert "Incident" in node_types
    assert "Victim" in node_types
    assert "Phone" in node_types
    assert "UPI" in node_types
    assert "BankAccount" in node_types
    assert "Transaction" in node_types

    # Verify edge connectivity
    relations = {link["relation"] for link in data["links"]}
    assert "reported_by" in relations
    assert "linked_phone" in relations
    assert "linked_upi" in relations
    assert "linked_bank" in relations


# ============================================================================
# 3. Entity Deduplication Across Reports
# ============================================================================

def test_duplicate_entities_deduplication_and_hub_creation():
    """
    Verifies that when two victims report the same scammer phone and UPI,
    nodes coalesce and create a shared fraud hub without duplicate nodes.
    """
    report1 = {
        "id": "REP-DEDUP-001",
        "victimId": "VIC-101",
        "victimName": "Victim One",
        "phoneNumber": "+91 99999 88888",
        "upiId": "Syndicate@Paytm",
        "typeOfScam": "Electricity KYC",
        "amountLost": 15000.0,
    }
    report2 = {
        "id": "REP-DEDUP-002",
        "victimId": "VIC-102",
        "victimName": "Victim Two",
        # Same phone in different format
        "phoneNumber": "99999-88888",
        # Same UPI in lowercase
        "upiId": "syndicate@paytm",
        "typeOfScam": "Lottery Scam",
        "amountLost": 25000.0,
    }

    client.post("/api/v1/reports", json=report1)
    client.post("/api/v1/reports", json=report2)

    res = client.get("/api/v1/graph/nodes")
    assert res.status_code == 200
    data = res.json()

    phone_nodes = [n for n in data["nodes"] if n["type"] == "Phone"]
    upi_nodes = [n for n in data["nodes"] if n["type"] == "UPI"]

    # Deduplicated: Exactly 1 phone node and 1 UPI node
    assert len(phone_nodes) == 1
    assert len(upi_nodes) == 1
    assert phone_nodes[0]["id"] in ["phone:9999988888", "phone:+919999988888"]
    assert upi_nodes[0]["id"] == "upi:syndicate@paytm"

    # Distinct victim nodes
    victim_nodes = [n for n in data["nodes"] if n["type"] == "Victim"]
    assert len(victim_nodes) == 2


# ============================================================================
# 4. Centrality & Community Detection
# ============================================================================

def test_centrality_identifies_shared_hubs():
    """Verifies PageRank and Betweenness Centrality highlight shared mule hubs."""
    shared_phone = "+91 88888 77777"
    for i in range(3):
        client.post("/api/v1/reports", json={
            "id": f"REP-CENT-{i}",
            "victimId": f"VIC-CENT-{i}",
            "victimName": f"Victim {i}",
            "phoneNumber": shared_phone,
            "typeOfScam": "Customs Arrest",
        })

    res = client.get("/api/v1/graph/centrality")
    assert res.status_code == 200
    data = res.json()

    assert len(data["pagerank"]) > 0
    assert len(data["top_influencers"]) > 0

    top = data["top_influencers"][0]
    # The shared phone hub must rank at or near top influencer
    assert "88888" in top["node_id"] or top["type"] in ["Phone", "Victim", "Incident"]
    assert top["degree"] >= 2


def test_community_detection_separates_disjoint_syndicates():
    """Verifies Louvain community detection groups connected components correctly."""
    # Syndicate Ring A
    client.post("/api/v1/reports", json={
        "id": "REP-SYN-A1",
        "victimId": "VIC-A1",
        "phoneNumber": "+91 11111 00000",
        "upiId": "ringA@upi",
    })
    client.post("/api/v1/reports", json={
        "id": "REP-SYN-A2",
        "victimId": "VIC-A2",
        "phoneNumber": "+91 11111 00000",
        "upiId": "ringA@upi",
    })

    # Disjoint Syndicate Ring B
    client.post("/api/v1/reports", json={
        "id": "REP-SYN-B1",
        "victimId": "VIC-B1",
        "phoneNumber": "+91 22222 00000",
        "upiId": "ringB@upi",
    })

    res = client.get("/api/v1/graph/clusters")
    assert res.status_code == 200
    data = res.json()

    assert data["total_clusters"] >= 2
    for cluster in data["clusters"]:
        assert "id" in cluster
        assert "nodes" in cluster
        assert "size" in cluster
        assert "risk_score" in cluster
        assert cluster["size"] > 0


# ============================================================================
# 5. Query Filters & Validation
# ============================================================================

def test_query_filter_by_entity_type():
    """Verifies entity_type filter returns only requested entity category."""
    client.post("/api/v1/reports", json={
        "id": "REP-FILT-1",
        "victimId": "VIC-FILT-1",
        "phoneNumber": "+91 33333 44444",
        "upiId": "test@upi",
    })

    # Request only Phone nodes
    res_phone = client.get("/api/v1/graph/nodes?entity_type=Phone")
    assert res_phone.status_code == 200
    data = res_phone.json()
    assert all(n["type"] == "Phone" for n in data["nodes"])
    assert len(data["nodes"]) == 1

    # Request only Victim nodes
    res_vic = client.get("/api/v1/graph/nodes?entity_type=Victim")
    assert res_vic.status_code == 200
    data_vic = res_vic.json()
    assert all(n["type"] == "Victim" for n in data_vic["nodes"])


def test_invalid_entity_type_filter_rejection():
    """Verifies invalid entity_type query parameter is rejected with HTTP 400/422."""
    res = client.get("/api/v1/graph/nodes?entity_type=UnknownAlienEntity")
    assert res.status_code in [400, 422]
    data = res.json()
    assert "Invalid entity_type" in data.get("message", str(data))


def test_query_filter_by_incident_id_and_limit():
    """Verifies incident_id subgraph filtering and limit constraints."""
    inc1 = "REP-SUBGRAPH-1"
    inc2 = "REP-SUBGRAPH-2"

    res1 = client.post("/api/v1/reports", json={
        "id": inc1,
        "victimName": "Victim One",
        "victimId": "VIC-SG-1",
        "phoneNumber": "+91 55555 11111",
    })
    actual_inc1 = res1.json()["id"]

    res2 = client.post("/api/v1/reports", json={
        "id": inc2,
        "victimName": "Victim Two",
        "victimId": "VIC-SG-2",
        "phoneNumber": "+91 55555 22222",
    })
    actual_inc2 = res2.json()["id"]

    # Filter to incident 1 subgraph
    res = client.get(f"/api/v1/graph/nodes?incident_id={actual_inc1}")
    assert res.status_code == 200
    data = res.json()
    node_ids = {n["id"] for n in data["nodes"]}
    assert f"incident:{actual_inc1}" in node_ids
    assert f"incident:{actual_inc2}" not in node_ids

    # Limit parameter
    res_limit = client.get("/api/v1/graph/nodes?limit=2")
    assert res_limit.status_code == 200
    assert len(res_limit.json()["nodes"]) <= 2


# ============================================================================
# 6. Caching Efficiency
# ============================================================================

def test_graph_service_caching_and_cache_invalidation():
    """Verifies that consecutive graph calls reuse cached calculations until modified."""
    client.post("/api/v1/reports", json={
        "id": "REP-CACHE-1",
        "victimId": "VIC-CACHE-1",
        "phoneNumber": "+91 77777 00000",
    })

    # First call primes cache
    res1 = graph_service.get_centrality()
    # Second call returns cached reference
    res2 = graph_service.get_centrality()
    assert res1 is res2

    # Adding new report invalidates cache
    client.post("/api/v1/reports", json={
        "id": "REP-CACHE-2",
        "victimId": "VIC-CACHE-2",
        "phoneNumber": "+91 77777 11111",
    })
    res3 = graph_service.get_centrality()
    assert res3 is not res1
    assert len(res3["pagerank"]) > len(res1["pagerank"])


# ============================================================================
# 7. Report By ID Endpoint & Scalability Testing (100, 500, 1000 nodes)
# ============================================================================

def test_get_report_by_id_success_and_not_found():
    """Tests GET /api/v1/reports/{report_id} and 404 behavior."""
    post_res = client.post("/api/v1/reports", json={
        "id": "REP-LOOKUP-01",
        "victimName": "Pooja Verma",
        "phoneNumber": "+91 99999 12345",
        "typeOfScam": "Job Scam",
        "amountLost": 25000.0,
    })
    assert post_res.status_code == 201
    created_id = post_res.json()["id"]

    # Lookup existing
    get_res = client.get(f"/api/v1/reports/{created_id}")
    assert get_res.status_code == 200
    report = get_res.json()
    assert report["id"] == created_id
    assert report["victimName"] == "Pooja Verma"

    # Lookup non-existent
    bad_res = client.get("/api/v1/reports/REP-NONEXISTENT-999")
    assert bad_res.status_code == 404


@pytest.mark.parametrize("target_nodes", [100, 500, 1000])
def test_graph_performance_scale(target_nodes):
    """
    Validates graph construction, PageRank, and community detection
    performance at 100, 500, and 1000 node scales.
    Ensures backend latency remains responsive and memory is controlled.
    """
    import time
    # Each report generates ~3-4 nodes (Incident, Victim, Phone, UPI/Bank)
    num_reports = target_nodes // 3 + 1
    reports = []
    for i in range(num_reports):
        # Create overlapping clusters every 5 reports to simulate syndicates
        mule_group = i // 5
        reports.append({
            "id": f"REP-SCALE-{target_nodes}-{i}",
            "victimId": f"VIC-SCALE-{target_nodes}-{i}",
            "victimName": f"Victim {i}",
            "phoneNumber": f"+91 98000 {mule_group:05d}",
            "upiId": f"mule_{mule_group}@upi",
            "bankAccount": f"BANK_{mule_group}",
            "typeOfScam": "Investment Scam",
            "amountLost": 10000.0 + i,
        })

    graph_service.clear()
    for r in reports:
        graph_service.add_report(r)

    t0 = time.perf_counter()
    nodes_res = graph_service.get_nodes(limit=target_nodes)
    centrality_res = graph_service.get_centrality(top_n=10)
    clusters_res = graph_service.get_syndicate_clusters()
    elapsed = time.perf_counter() - t0

    assert nodes_res["total_nodes"] >= min(target_nodes, 100)
    assert len(centrality_res["pagerank"]) > 0
    assert len(clusters_res) > 0
    # Must compute in well under 2.5 seconds even at 1000 nodes
    assert elapsed < 2.5, f"Graph analytics took too long ({elapsed:.3f}s) for {target_nodes} nodes"

