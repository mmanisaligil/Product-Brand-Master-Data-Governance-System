from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class SKUCreate(BaseModel):
    brand: str
    canonical_name: str
    category: str


class SKUAliasCreate(BaseModel):
    alias_type: str
    alias_value: str


class SKUAliasOut(BaseModel):
    alias_type: str
    alias_value: str

    class Config:
        from_attributes = True


class SKUOut(BaseModel):
    id: str
    brand: str
    canonical_name: str
    category: str
    status: str
    aliases: List[SKUAliasOut] = []

    class Config:
        from_attributes = True


class EvidenceCreate(BaseModel):
    evidence_id: Optional[str] = None
    source_type: str
    captured_at: datetime
    issuer: str
    page_section: Optional[str] = None
    reliability_score: float


class EvidenceOut(BaseModel):
    id: str
    source_type: str
    file_hash: str
    captured_at: datetime
    issuer: str
    page_section: Optional[str] = None
    reliability_score: float

    class Config:
        from_attributes = True


class FieldValueOut(BaseModel):
    id: int
    sku_id: str
    evidence_id: str
    field_name: str
    value: str
    unit: Optional[str]
    confidence: float
    status: str
    needs_review: bool

    class Config:
        from_attributes = True


class ERDecisionOut(BaseModel):
    sku_id: str
    match_score: float
    match_explanation: str
    needs_review: bool
    decision_source: str


class ExportResult(BaseModel):
    export_path: Optional[str]
    blocked_fields: Optional[List[str]] = None
    message: str
