# packages/ai-graph/rakshagrid/ai_graph/models/entity.py
"""Entity definitions and types for Fraud Network Graph Intelligence."""

from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class EntityType(str, Enum):
    VICTIM = "Victim"
    PHONE = "Phone"
    UPI = "UPI"
    BANK_ACCOUNT = "BankAccount"
    TRANSACTION = "Transaction"
    INCIDENT = "Incident"

    @classmethod
    def has_value(cls, val: str) -> bool:
        return any(val.lower() == item.value.lower() for item in cls)

    @classmethod
    def from_str(cls, val: str) -> "EntityType":
        for item in cls:
            if item.value.lower() == val.lower():
                return item
        raise ValueError(f"Unknown entity type: {val}")


class GraphNode(BaseModel):
    id: str = Field(..., description="Unique node identifier, e.g., 'phone:+919876543210'")
    type: EntityType = Field(..., description="Entity classification")
    label: str = Field(..., description="Human-readable node label")
    properties: Dict[str, Any] = Field(default_factory=dict, description="Metadata attributes")


class GraphLink(BaseModel):
    source: str = Field(..., description="Source node id")
    target: str = Field(..., description="Target node id")
    relation: str = Field(..., description="Edge relation type (e.g., 'linked_phone', 'reported_by')")
    weight: float = Field(default=1.0, description="Edge weight")
