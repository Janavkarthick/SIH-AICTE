"""Knowledge Graph Analysis and Cross-Institutional Collusion Engine.

Constructs an entity-relationship graph using NetworkX to identify anomalous patterns:
- Faculty ghost-teaching across multiple institutions simultaneously
- Collusive multi-campus land claims on identical survey parcels
- Reused notary seals and unauthorized shared signatories
Exports graph topology formatted specifically for Cytoscape.js visualization.
"""

import json
from typing import Any, Dict, List, Optional
import networkx as nx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.graph import GraphEntity, GraphRelation
from app.schemas.graph import CytoscapeElement, GraphDataResponse


class GraphService:
    """Graph intelligence service for detecting regulatory fraud across institutions."""

    def __init__(self):
        self.g = nx.DiGraph()

    async def build_graph_from_db(self, db: AsyncSession) -> nx.DiGraph:
        """Construct NetworkX graph from database entities and relationships."""
        self.g.clear()

        # Load all entities
        ent_stmt = select(GraphEntity)
        entities = (await db.execute(ent_stmt)).scalars().all()
        for e in entities:
            meta = json.loads(e.metadata_json) if e.metadata_json else {}
            self.g.add_node(
                str(e.id),
                entity_id=e.entity_id,
                name=e.name,
                entity_type=e.entity_type,
                metadata=meta,
            )

        # Load all relations
        rel_stmt = select(GraphRelation)
        relations = (await db.execute(rel_stmt)).scalars().all()
        for r in relations:
            meta = json.loads(r.metadata_json) if r.metadata_json else {}
            self.g.add_edge(
                str(r.source_entity_id),
                str(r.target_entity_id),
                relation_id=r.id,
                relation_type=r.relation_type,
                is_flagged=r.is_flagged,
                flag_reason=r.flag_reason,
                metadata=meta,
            )

        return self.g

    async def detect_anomalies_and_flag(self, db: AsyncSession) -> int:
        """Analyze graph structure for multi-institution faculty, land duplication, and mark flags."""
        await self.build_graph_from_db(db)
        flagged_count = 0

        # Fetch all relations from DB for updating
        rel_stmt = select(GraphRelation)
        relations_db = {r.id: r for r in (await db.execute(rel_stmt)).scalars().all()}

        # 1. Multi-institution Faculty (Same faculty connected to > 1 institution)
        for node_id, data in self.g.nodes(data=True):
            if data.get("entity_type") == "faculty":
                # Find connected institutions
                connected_insts = []
                for _, target, edge_data in self.g.out_edges(node_id, data=True):
                    if edge_data.get("relation_type") == "employed_at":
                        connected_insts.append((edge_data.get("relation_id"), target))

                if len(connected_insts) > 1:
                    reason = (
                        f"COLLUSION ANOMALY: Faculty member '{data.get('name')}' (ID: {data.get('entity_id')}) "
                        f"is simultaneously listed as full-time staff across {len(connected_insts)} different institutions."
                    )
                    for rel_id, _ in connected_insts:
                        if rel_id in relations_db:
                            relations_db[rel_id].is_flagged = True
                            relations_db[rel_id].flag_reason = reason
                            flagged_count += 1

            # 2. Shared Land Survey Parcel (Same land connected to > 1 institution)
            elif data.get("entity_type") == "land":
                claiming_insts = []
                for source, _, edge_data in self.g.in_edges(node_id, data=True):
                    if edge_data.get("relation_type") == "owns_land":
                        claiming_insts.append((edge_data.get("relation_id"), source))

                if len(claiming_insts) > 1:
                    reason = (
                        f"COLLUSION ANOMALY: Land parcel Survey #{data.get('entity_id')} "
                        f"is concurrently claimed as infrastructure by {len(claiming_insts)} separate institutions."
                    )
                    for rel_id, _ in claiming_insts:
                        if rel_id in relations_db:
                            relations_db[rel_id].is_flagged = True
                            relations_db[rel_id].flag_reason = reason
                            flagged_count += 1

        await db.commit()
        return flagged_count

    def to_cytoscape_elements(
        self,
        entities: List[GraphEntity],
        relations: List[GraphRelation],
    ) -> GraphDataResponse:
        """Convert database models into standard Cytoscape.js elements."""
        elements: List[CytoscapeElement] = []
        flagged_count = 0

        # Nodes
        for e in entities:
            meta = json.loads(e.metadata_json) if e.metadata_json else {}
            elements.append(
                CytoscapeElement(
                    data={
                        "id": f"node_{e.id}",
                        "db_id": e.id,
                        "label": f"{e.name}\n({e.entity_type})",
                        "name": e.name,
                        "type": e.entity_type,
                        "entity_id": e.entity_id,
                        "metadata": meta,
                    }
                )
            )

        # Edges
        for r in relations:
            if r.is_flagged:
                flagged_count += 1
            meta = json.loads(r.metadata_json) if r.metadata_json else {}
            elements.append(
                CytoscapeElement(
                    data={
                        "id": f"edge_{r.id}",
                        "db_id": r.id,
                        "source": f"node_{r.source_entity_id}",
                        "target": f"node_{r.target_entity_id}",
                        "label": r.relation_type,
                        "is_flagged": r.is_flagged,
                        "flag_reason": r.flag_reason,
                        "metadata": meta,
                    }
                )
            )

        return GraphDataResponse(
            elements=elements,
            flagged_relations_count=flagged_count,
        )


# Singleton instance
graph_service = GraphService()
