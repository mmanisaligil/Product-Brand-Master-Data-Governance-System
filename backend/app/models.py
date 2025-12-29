from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .db import Base

class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(String, primary_key=True)
    source_type = Column(String, nullable=False)
    file_hash = Column(String, nullable=False)
    capture_date = Column(DateTime, nullable=False)
    issuer = Column(String, nullable=False)
    scope = Column(String, nullable=True)
    page_section = Column(String, nullable=True)
    reliability_score = Column(Float, nullable=False)
    file_path = Column(String, nullable=False)

    field_candidates = relationship("FieldCandidate", back_populates="evidence")

class SKU(Base):
    __tablename__ = "skus"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    status = Column(String, nullable=False, default="draft")

    aliases = relationship("SKUAlias", back_populates="sku")
    field_candidates = relationship("FieldCandidate", back_populates="sku")

class SKUAlias(Base):
    __tablename__ = "sku_aliases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sku_id = Column(String, ForeignKey("skus.id"), nullable=False)
    alias_type = Column(String, nullable=False)
    alias_value = Column(String, nullable=False)

    sku = relationship("SKU", back_populates="aliases")

class ERDecision(Base):
    __tablename__ = "er_decisions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    evidence_id = Column(String, ForeignKey("evidence.id"), nullable=False)
    sku_id = Column(String, ForeignKey("skus.id"), nullable=False)
    match_score = Column(Float, nullable=False)
    match_explanation = Column(Text, nullable=False)
    needs_review = Column(Boolean, default=False)
    decision_source = Column(String, nullable=False)
    locked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class FieldCandidate(Base):
    __tablename__ = "field_candidates"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sku_id = Column(String, ForeignKey("skus.id"), nullable=False)
    evidence_id = Column(String, ForeignKey("evidence.id"), nullable=False)
    field_name = Column(String, nullable=False)
    raw_value = Column(String, nullable=False)
    normalized_value = Column(String, nullable=True)
    confidence = Column(Float, nullable=False)
    status = Column(String, nullable=False, default="draft")
    needs_review = Column(Boolean, default=False)

    sku = relationship("SKU", back_populates="field_candidates")
    evidence = relationship("Evidence", back_populates="field_candidates")

class ConflictLog(Base):
    __tablename__ = "conflict_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sku_id = Column(String, ForeignKey("skus.id"), nullable=False)
    field_name = Column(String, nullable=False)
    resolution = Column(String, nullable=False)
    chosen_candidate_id = Column(Integer, ForeignKey("field_candidates.id"), nullable=True)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ChangeLog(Base):
    __tablename__ = "change_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    evidence_id = Column(String, ForeignKey("evidence.id"), nullable=False)
    field_name = Column(String, nullable=False)
    old_value = Column(String, nullable=True)
    new_value = Column(String, nullable=True)
    diff_note = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Versioning(Base):
    __tablename__ = "versioning"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sku_id = Column(String, ForeignKey("skus.id"), nullable=False)
    master_version = Column(Integer, nullable=False)
    export_version = Column(Integer, nullable=False)
    last_exported_at = Column(DateTime(timezone=True), nullable=True)
    exported_by = Column(String, nullable=True)
    change_type = Column(String, nullable=False)
