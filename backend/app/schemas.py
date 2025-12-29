from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class EvidenceCreate(BaseModel):
    evidence_id: Optional[str] = None
    source_type: str
    capture_date: datetime
    issuer: str
    scope: Optional[str] = None
    page_section: Optional[str] = None
    reliability_score: float

class EvidenceOut(BaseModel):
    id: str
    source_type: str
    file_hash: str
    capture_date: datetime
    issuer: str
    scope: Optional[str] = None
    page_section: Optional[str] = None
    reliability_score: float

    class Config:
        from_attributes = True

class ERResolveRequest(BaseModel):
    evidence_id: str
    observed_identifiers: List[str]
    row_hint: Optional[str] = None

class ERDecisionOut(BaseModel):
    sku_id: str
    match_score: float
    match_explanation: str
    needs_review: bool
    decision_source: str

class FieldCandidateOut(BaseModel):
    id: int
    sku_id: str
    evidence_id: str
    field_name: str
    raw_value: str
    normalized_value: Optional[str]
    confidence: float
    status: str
    needs_review: bool

    class Config:
        from_attributes = True

class SKUStatusOut(BaseModel):
    sku_id: str
    name: str
    status: str

class ExportResult(BaseModel):
    export_path: Optional[str]
    blocked_fields: Optional[List[str]] = None
    message: str
