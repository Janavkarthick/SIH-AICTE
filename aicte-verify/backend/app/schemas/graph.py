"""Pydantic schemas for knowledge graph representation and collusion detection."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict


class GraphEntityResponse(BaseModel):
    """Node in cross-institutional entity graph."""
    id: int
    entity_type: str
    entity_id: str
    name: str
    metadata_json: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class GraphRelationResponse(BaseModel):
    """Edge connecting entities in graph."""
    id: int
    source_entity_id: int
    target_entity_id: int
    relation_type: str
    metadata_json: Optional[str] = None
    is_flagged: bool
    flag_reason: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class CytoscapeNodeData(BaseModel):
    """Cytoscape.js node data payload."""
    id: str
    label: str
    type: str
    metadata: Dict[str, Any] = {}


class CytoscapeEdgeData(BaseModel):
    """Cytoscape.js edge data payload."""
    id: str
    source: str
    target: str
    label: str
    is_flagged: bool = False
    flag_reason: Optional[str] = None


class CytoscapeElement(BaseModel):
    """Standard Cytoscape element wrapper."""
    data: Dict[str, Any]


class GraphDataResponse(BaseModel):
    """Full graph structure formatted for Cytoscape.js visualization."""
    elements: List[CytoscapeElement]
    flagged_relations_count: int
