"""Knowledge graph entity and relationship models for cross-institutional collusion detection."""

from typing import Optional
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base


class GraphEntity(Base):
    """Node in cross-institutional entity relationship network."""
    __tablename__ = "graph_entities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    entity_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )  # institution, faculty, land, trust, signatory, stamp
    entity_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default="{}")

    # Outgoing and incoming relations
    outgoing_relations = relationship(
        "GraphRelation",
        foreign_keys="GraphRelation.source_entity_id",
        back_populates="source",
        cascade="all, delete-orphan",
    )
    incoming_relations = relationship(
        "GraphRelation",
        foreign_keys="GraphRelation.target_entity_id",
        back_populates="target",
        cascade="all, delete-orphan",
    )


class GraphRelation(Base):
    """Directed edge representing institutional affiliation, asset ownership, or shared signatory."""
    __tablename__ = "graph_relations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    source_entity_id: Mapped[int] = mapped_column(Integer, ForeignKey("graph_entities.id", ondelete="CASCADE"), nullable=False, index=True)
    target_entity_id: Mapped[int] = mapped_column(Integer, ForeignKey("graph_entities.id", ondelete="CASCADE"), nullable=False, index=True)
    relation_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )  # employed_at, owns_land, governed_by, signed_by, stamped_by
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True, default="{}")
    is_flagged: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    flag_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    source = relationship("GraphEntity", foreign_keys=[source_entity_id], back_populates="outgoing_relations")
    target = relationship("GraphEntity", foreign_keys=[target_entity_id], back_populates="incoming_relations")
