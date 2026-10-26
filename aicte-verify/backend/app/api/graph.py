"""Knowledge graph exploration and collusion detection endpoints."""

from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.graph import GraphEntity, GraphRelation
from app.models.user import User
from app.schemas.graph import (
    GraphDataResponse,
    GraphEntityResponse,
    GraphRelationResponse,
)
from app.services.graph.service import graph_service

router = APIRouter(prefix="/graph", tags=["Knowledge Graph"])


@router.get("", response_model=GraphDataResponse, include_in_schema=False)
@router.get("/", response_model=GraphDataResponse)
async def get_full_graph(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve all entity nodes and relationships formatted for Cytoscape.js."""
    all_e = list((await db.execute(select(GraphEntity))).scalars().all())
    all_r = list((await db.execute(select(GraphRelation))).scalars().all())
    return graph_service.to_cytoscape_elements(all_e, all_r)


@router.get("/entities", response_model=List[GraphEntityResponse])

async def get_graph_entities(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve all nodes in the cross-institutional entity graph."""
    stmt = select(GraphEntity)
    entities = list((await db.execute(stmt)).scalars().all())
    return [GraphEntityResponse.model_validate(e) for e in entities]


@router.get("/relations", response_model=List[GraphRelationResponse])
async def get_graph_relations(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve all directional relationships connecting entities."""
    stmt = select(GraphRelation)
    relations = list((await db.execute(stmt)).scalars().all())
    return [GraphRelationResponse.model_validate(r) for r in relations]


@router.get("/institution/{institution_id}", response_model=GraphDataResponse)
async def get_institution_subgraph(
    institution_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve neighborhood subgraph for an institution formatted for Cytoscape.js."""
    # Find entity for institution
    ent_stmt = select(GraphEntity).where(
        GraphEntity.entity_type == "institution",
        (GraphEntity.id == institution_id) | (GraphEntity.entity_id == str(institution_id)),
    )
    inst_node = (await db.execute(ent_stmt)).scalar_one_or_none()

    if not inst_node:
        # Fallback to returning all entities if specific entity ID match is unavailable
        all_e = list((await db.execute(select(GraphEntity))).scalars().all())
        all_r = list((await db.execute(select(GraphRelation))).scalars().all())
        return graph_service.to_cytoscape_elements(all_e, all_r)

    # Find connected relations
    rel_stmt = select(GraphRelation).where(
        (GraphRelation.source_entity_id == inst_node.id) | (GraphRelation.target_entity_id == inst_node.id)
    )
    relations = list((await db.execute(rel_stmt)).scalars().all())

    connected_node_ids = set()
    connected_node_ids.add(inst_node.id)
    for r in relations:
        connected_node_ids.add(r.source_entity_id)
        connected_node_ids.add(r.target_entity_id)

    nodes_stmt = select(GraphEntity).where(GraphEntity.id.in_(connected_node_ids))
    entities = list((await db.execute(nodes_stmt)).scalars().all())

    return graph_service.to_cytoscape_elements(entities, relations)


@router.get("/flagged", response_model=GraphDataResponse)
async def get_flagged_relationships(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve only collusive or anomalous flagged relationships."""
    # Run collusion detection scan
    await graph_service.detect_anomalies_and_flag(db)

    rel_stmt = select(GraphRelation).where(GraphRelation.is_flagged == True)
    flagged_relations = list((await db.execute(rel_stmt)).scalars().all())

    node_ids = set()
    for r in flagged_relations:
        node_ids.add(r.source_entity_id)
        node_ids.add(r.target_entity_id)

    if node_ids:
        nodes_stmt = select(GraphEntity).where(GraphEntity.id.in_(node_ids))
        entities = list((await db.execute(nodes_stmt)).scalars().all())
    else:
        entities = []

    return graph_service.to_cytoscape_elements(entities, flagged_relations)
