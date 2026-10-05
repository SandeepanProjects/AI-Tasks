import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, Integer, JSON, Boolean, UniqueConstraint, Index, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pgvector.sqlalchemy import Vector

class Base(DeclarativeBase): pass

class ReviewRow(Base):
    __tablename__="reviews"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True), primary_key=True)
    tenant_id: Mapped[str]=mapped_column(String(128), index=True)
    created_by: Mapped[str]=mapped_column(String(256))
    question: Mapped[str]=mapped_column(Text)
    assets: Mapped[list]=mapped_column(JSON)
    lookback_days: Mapped[int]=mapped_column(Integer)
    purpose: Mapped[str]=mapped_column(String(40))
    status: Mapped[str]=mapped_column(String(40), index=True)
    report: Mapped[dict|None]=mapped_column(JSON, nullable=True)
    reviewer_id: Mapped[str|None]=mapped_column(String(256), nullable=True)
    reviewer_comment: Mapped[str|None]=mapped_column(Text, nullable=True)
    version: Mapped[int]=mapped_column(Integer, default=1)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), server_default=func.now())
    __table_args__=(UniqueConstraint("tenant_id","id",name="uq_review_tenant_id"),)

class IdempotencyRow(Base):
    __tablename__="idempotency_keys"
    key: Mapped[str]=mapped_column(String(256), primary_key=True)
    tenant_id: Mapped[str]=mapped_column(String(128), index=True)
    review_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True))
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), server_default=func.now())

class EvidenceChunkRow(Base):
    __tablename__="evidence_chunks"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[str]=mapped_column(String(128), index=True)
    source_name: Mapped[str]=mapped_column(String(256))
    source_uri: Mapped[str]=mapped_column(Text)
    observed_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), index=True)
    content: Mapped[str]=mapped_column(Text)
    content_hash: Mapped[str]=mapped_column(String(64), index=True)
    embedding: Mapped[list|None]=mapped_column(Vector(384), nullable=True)
    metadata_json: Mapped[dict]=mapped_column("metadata", JSON, default=dict)
    __table_args__=(Index("ix_evidence_tenant_observed","tenant_id","observed_at"),)

class AuditEventRow(Base):
    __tablename__="audit_events"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Mapped[str]=mapped_column(String(128), index=True)
    actor_id: Mapped[str]=mapped_column(String(256))
    action: Mapped[str]=mapped_column(String(128))
    resource_id: Mapped[str]=mapped_column(String(128), index=True)
    details: Mapped[dict]=mapped_column(JSON, default=dict)
    occurred_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)

class WorkflowCheckpointRow(Base):
    __tablename__="workflow_checkpoints"
    id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    review_id: Mapped[uuid.UUID]=mapped_column(UUID(as_uuid=True), index=True)
    node: Mapped[str]=mapped_column(String(128))
    state: Mapped[dict]=mapped_column(JSON)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True), server_default=func.now())
