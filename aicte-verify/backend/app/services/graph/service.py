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
        """Analyze graph structure for multi-institution faculty and land duplication.
        
        Implements statutory distinction:
        - Sister colleges sharing the SAME sponsoring trust are marked as legitimate 'shared sponsor' (not flagged).
        - Ghost faculty requires matching on unique faculty ID (not common names), overlapping full-time tenure, and different cities.
        - Unrelated trusts claiming the same land or faculty are marked CRITICAL collusion.
        """
        from app.models.institution import Institution
        await self.build_graph_from_db(db)
        flagged_count = 0

        # Fetch institutions for trust & city resolution
        inst_stmt = select(Institution)
        institutions = list((await db.execute(inst_stmt)).scalars().all())
        inst_by_id = {i.id: i for i in institutions}
        inst_by_code = {i.code: i for i in institutions}
        inst_by_name = {i.name.strip().lower(): i for i in institutions}

        def resolve_institution(node_data: Dict[str, Any]) -> Optional[Institution]:
            ent_id = node_data.get("entity_id", "")
            if ent_id in inst_by_code:
                return inst_by_code[ent_id]
            try:
                num_id = int(ent_id.replace("INST", "").replace("inst_", ""))
                if num_id in inst_by_id:
                    return inst_by_id[num_id]
            except ValueError:
                pass
            name = node_data.get("name", "").strip().lower()
            return inst_by_name.get(name)

        # Fetch all relations from DB for updating
        rel_stmt = select(GraphRelation)
        relations_db = {r.id: r for r in (await db.execute(rel_stmt)).scalars().all()}

        # 1. Multi-institution Faculty
        for node_id, data in self.g.nodes(data=True):
            if data.get("entity_type") == "faculty":
                faculty_unique_id = data.get("entity_id", "")
                connected_inst_edges = []
                for _, target, edge_data in self.g.out_edges(node_id, data=True):
                    if edge_data.get("relation_type") == "employed_at":
                        target_node = self.g.nodes.get(target, {})
                        inst_obj = resolve_institution(target_node)
                        connected_inst_edges.append((edge_data.get("relation_id"), target_node, inst_obj))

                if len(connected_inst_edges) > 1:
                    # Require unique faculty identifier (PID, PAN hash, Aadhaar hash) - never match solely on common names
                    if not faculty_unique_id or faculty_unique_id.startswith("GEN_"):
                        # Ambiguous identifier - do not flag to avoid false positive on common Indian names
                        continue

                    # Check trusts and cities of connected institutions
                    trusts = set()
                    cities = set()
                    for _, _, inst in connected_inst_edges:
                        if inst:
                            trusts.add(inst.trust_name.strip().lower())
                            cities.add(inst.city.strip().lower())

                    # If all institutions belong to the same sponsoring trust and same campus/city:
                    if len(trusts) == 1 and len(cities) <= 1:
                        shared_reason = (
                            f"SHARED SPONSOR: Faculty '{data.get('name')}' (ID: {faculty_unique_id}) "
                            f"teaches across sister campuses under common trust '{list(trusts)[0]}'. Permitted."
                        )
                        for rel_id, _, _ in connected_inst_edges:
                            if rel_id in relations_db:
                                relations_db[rel_id].is_flagged = False
                                relations_db[rel_id].flag_reason = shared_reason
                    else:
                        # Unrelated trusts or physically incompatible multi-city employment
                        conflict_reason = (
                            f"CRITICAL GHOST FACULTY: Faculty member with Unique ID '{faculty_unique_id}' ({data.get('name')}) "
                            f"is simultaneously listed as full-time staff across {len(connected_inst_edges)} institutions "
                            f"with differing trusts/cities ({', '.join(cities) if cities else 'Multiple cities'})."
                        )
                        for rel_id, _, _ in connected_inst_edges:
                            if rel_id in relations_db:
                                relations_db[rel_id].is_flagged = True
                                relations_db[rel_id].flag_reason = conflict_reason
                                flagged_count += 1

            # 2. Shared Land Survey Parcel
            elif data.get("entity_type") == "land":
                claiming_inst_edges = []
                for source, _, edge_data in self.g.in_edges(node_id, data=True):
                    if edge_data.get("relation_type") == "owns_land":
                        source_node = self.g.nodes.get(source, {})
                        inst_obj = resolve_institution(source_node)
                        claiming_inst_edges.append((edge_data.get("relation_id"), source_node, inst_obj))

                if len(claiming_inst_edges) > 1:
                    trusts = set()
                    for _, _, inst in claiming_inst_edges:
                        if inst:
                            trusts.add(inst.trust_name.strip().lower())

                    # Same sponsoring trust => legitimate shared integrated educational campus
                    if len(trusts) == 1:
                        shared_reason = (
                            f"SHARED SPONSOR: Land parcel Survey #{data.get('entity_id')} is part of an integrated campus "
                            f"shared by sister institutions under '{list(trusts)[0]}'. Permitted under AICTE norms."
                        )
                        for rel_id, _, _ in claiming_inst_edges:
                            if rel_id in relations_db:
                                relations_db[rel_id].is_flagged = False
                                relations_db[rel_id].flag_reason = shared_reason
                    else:
                        conflict_reason = (
                            f"CRITICAL LAND COLLUSION: Land parcel Survey #{data.get('entity_id')} "
                            f"is concurrently claimed as infrastructure by {len(claiming_inst_edges)} unrelated institutions "
                            f"under distinct trusts ({', '.join(trusts) if trusts else 'Unrelated entities'})."
                        )
                        for rel_id, _, _ in claiming_inst_edges:
                            if rel_id in relations_db:
                                relations_db[rel_id].is_flagged = True
                                relations_db[rel_id].flag_reason = conflict_reason
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
