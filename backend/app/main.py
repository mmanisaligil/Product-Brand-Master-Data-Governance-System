import hashlib
import os
from datetime import datetime
from fastapi import FastAPI, Depends, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from .db import get_db
from .models import Evidence, FieldCandidate, SKU, ERDecision, ChangeLog
from .schemas import EvidenceOut, ERResolveRequest, ERDecisionOut, FieldCandidateOut, SKUStatusOut, ExportResult
from .modules.extraction.extractor import extract_fields
from .modules.normalization.normalizer import normalize_field
from .modules.er.engine import resolve_entities, store_decision
from .modules.qa.quality import resolve_conflicts
from .modules.export.exporter import generate_export

app = FastAPI(title="Product & Brand Master Data Governance System")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

EVIDENCE_DIR = os.getenv("EVIDENCE_DIR", "/data/evidence")
EXPORT_DIR = os.getenv("EXPORT_DIR", "/data/exports")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/", response_class=HTMLResponse)
def index():
    with open("app/static/index.html", "r", encoding="utf-8") as handle:
        return handle.read()


def hash_file(file_path: str) -> str:
    hasher = hashlib.sha256()
    with open(file_path, "rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


@app.post("/evidence/upload", response_model=EvidenceOut)
def upload_evidence(
    source_type: str = Form(...),
    capture_date: str = Form(...),
    issuer: str = Form(...),
    reliability_score: float = Form(...),
    scope: str = Form(None),
    page_section: str = Form(None),
    evidence_id: str = Form(None),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    file_path = os.path.join(EVIDENCE_DIR, file.filename)
    with open(file_path, "wb") as handle:
        handle.write(file.file.read())

    file_hash = hash_file(file_path)
    capture_dt = datetime.fromisoformat(capture_date)

    existing = None
    if evidence_id:
        existing = db.query(Evidence).filter(Evidence.id == evidence_id).first()

    if existing:
        if existing.file_hash != file_hash:
            existing.file_hash = file_hash
            existing.file_path = file_path
            existing.capture_date = capture_dt
            db.query(FieldCandidate).filter(FieldCandidate.evidence_id == existing.id).update(
                {"status": "draft", "needs_review": True}
            )
            db.add(
                ChangeLog(
                    evidence_id=existing.id,
                    field_name="*",
                    old_value="previous",
                    new_value="updated",
                    diff_note="Evidence updated: fields invalidated for re-review.",
                )
            )
            db.commit()
        return existing

    evidence = Evidence(
        id=evidence_id or f"ev-{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}",
        source_type=source_type,
        file_hash=file_hash,
        capture_date=capture_dt,
        issuer=issuer,
        scope=scope,
        page_section=page_section,
        reliability_score=reliability_score,
        file_path=file_path,
    )
    db.add(evidence)
    db.commit()
    db.refresh(evidence)
    return evidence


@app.post("/extraction/run/{evidence_id}", response_model=list[FieldCandidateOut])
def run_extraction(evidence_id: str, db: Session = Depends(get_db)):
    evidence = db.query(Evidence).filter(Evidence.id == evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")

    extraction = extract_fields(evidence.file_path)
    candidates = []
    for candidate in extraction["candidates"]:
        normalized = normalize_field(candidate["field_name"], candidate["raw_value"])
        field_candidate = FieldCandidate(
            sku_id=evidence.scope or "unknown",
            evidence_id=evidence.id,
            field_name=candidate["field_name"],
            raw_value=candidate["raw_value"],
            normalized_value=normalized,
            confidence=0.8,
            status="draft",
            needs_review=extraction["needs_review"],
        )
        db.add(field_candidate)
        candidates.append(field_candidate)
    db.commit()
    return candidates


@app.post("/er/resolve", response_model=ERDecisionOut)
def resolve_er(payload: ERResolveRequest, db: Session = Depends(get_db)):
    sku_id, score, explanation, needs_review, source = resolve_entities(
        db, payload.evidence_id, payload.observed_identifiers
    )
    if not sku_id:
        raise HTTPException(status_code=404, detail="No candidate SKU found")
    decision = store_decision(db, payload.evidence_id, sku_id, score, explanation, needs_review, source)
    return ERDecisionOut(
        sku_id=decision.sku_id,
        match_score=decision.match_score,
        match_explanation=decision.match_explanation,
        needs_review=decision.needs_review,
        decision_source=decision.decision_source,
    )


@app.post("/er/confirm/{decision_id}")
def confirm_er(decision_id: int, db: Session = Depends(get_db)):
    decision = db.query(ERDecision).filter(ERDecision.id == decision_id).first()
    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")
    decision.locked = True
    decision.decision_source = "human_confirmed"
    decision.needs_review = False
    db.commit()
    return {"status": "confirmed"}


@app.get("/skus", response_model=list[SKUStatusOut])
def list_skus(db: Session = Depends(get_db)):
    skus = db.query(SKU).all()
    return [SKUStatusOut(sku_id=sku.id, name=sku.name, status=sku.status) for sku in skus]


@app.get("/fields/{sku_id}", response_model=list[FieldCandidateOut])
def get_fields(sku_id: str, db: Session = Depends(get_db)):
    candidates = db.query(FieldCandidate).filter(FieldCandidate.sku_id == sku_id).all()
    return candidates


@app.post("/qa/resolve/{sku_id}")
def resolve_sku_conflicts(sku_id: str, db: Session = Depends(get_db)):
    status, blocked = resolve_conflicts(db, sku_id)
    return {"status": status, "blocked_fields": blocked}


@app.post("/export/{sku_id}", response_model=ExportResult)
def export_sku(sku_id: str, exported_by: str = Form("system"), db: Session = Depends(get_db)):
    path, missing = generate_export(db, sku_id, EXPORT_DIR, exported_by)
    if missing:
        return ExportResult(export_path=None, blocked_fields=missing, message="Export blocked")
    return ExportResult(export_path=path, blocked_fields=None, message="Export generated")
