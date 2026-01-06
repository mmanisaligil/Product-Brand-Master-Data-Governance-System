from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .db import Base


class SKU(Base):
    __tablename__ = "skus"

    id = Column(String, primary_key=True)
    brand = Column(String, nullable=False)
    canonical_name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    status = Column(String, nullable=False, default="draft")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    aliases = relationship("SKUAlias", back_populates="sku")
    field_values = relationship("FieldValue", back_populates="sku")


class SKUAlias(Base):
    __tablename__ = "sku_aliases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sku_id = Column(String, ForeignKey("skus.id"), nullable=False)
    alias_type = Column(String, nullable=False)
    alias_value = Column(String, nullable=False)

    sku = relationship("SKU", back_populates="aliases")


class Evidence(Base):
    __tablename__ = "evidence"

    id = Column(String, primary_key=True)
    source_type = Column(String, nullable=False)
    issuer = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_hash = Column(String, nullable=False)
    reliability_score = Column(Float, nullable=False)
    captured_at = Column(DateTime(timezone=True), nullable=False)
    page_section = Column(String, nullable=True)

    field_values = relationship("FieldValue", back_populates="evidence")


class FieldValue(Base):
    __tablename__ = "field_values"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sku_id = Column(String, ForeignKey("skus.id"), nullable=False)
    field_name = Column(String, nullable=False)
    value = Column(String, nullable=False)
    unit = Column(String, nullable=True)
    confidence = Column(Float, nullable=False)
    evidence_id = Column(String, ForeignKey("evidence.id"), nullable=False)
    status = Column(String, nullable=False, default="draft")
    needs_review = Column(Boolean, default=False)

    sku = relationship("SKU", back_populates="field_values")
    evidence = relationship("Evidence", back_populates="field_values")


class ERDecision(Base):
    __tablename__ = "er_decisions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sku_id = Column(String, ForeignKey("skus.id"), nullable=False)
    match_score = Column(Float, nullable=False)
    match_explanation = Column(Text, nullable=False)
    decision_source = Column(String, nullable=False)
    needs_review = Column(Boolean, default=False)
    locked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ConflictLog(Base):
    __tablename__ = "conflict_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sku_id = Column(String, ForeignKey("skus.id"), nullable=False)
    field_name = Column(String, nullable=False)
    resolution = Column(String, nullable=False)
    chosen_field_value_id = Column(Integer, ForeignKey("field_values.id"), nullable=True)
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


class ExportEvent(Base):
    __tablename__ = "exports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    sku_id = Column(String, ForeignKey("skus.id"), nullable=False)
    export_version = Column(Integer, nullable=False)
    change_type = Column(String, nullable=False)
    exported_at = Column(DateTime(timezone=True), server_default=func.now())
