from typing import List, Tuple
from sqlalchemy.orm import Session
from ...models import FieldCandidate, ConflictLog, SKU

PRIORITY = {
    "manufacturer": 3,
    "official": 2,
    "broker": 1,
    "reseller": 0,
}

REQUIRED_FIELDS = {
    "gross_weight",
    "net_weight",
    "length",
    "width",
    "height",
    "capacity_wh",
    "inverter_w",
}


def infer_priority(evidence_source: str) -> int:
    for key, value in PRIORITY.items():
        if key in evidence_source.lower():
            return value
    return 0


def resolve_conflicts(db: Session, sku_id: str) -> Tuple[str, List[str]]:
    candidates = db.query(FieldCandidate).filter(FieldCandidate.sku_id == sku_id).all()
    blocked_fields = []
    status = "verified"

    grouped = {}
    for candidate in candidates:
        grouped.setdefault(candidate.field_name, []).append(candidate)

    for field_name, items in grouped.items():
        values = {item.normalized_value or item.raw_value for item in items}
        if len(values) == 1:
            for item in items:
                item.status = "verified"
                item.needs_review = False
        else:
            ranked = sorted(
                items,
                key=lambda item: (infer_priority(item.evidence.source_type), item.confidence),
                reverse=True,
            )
            top = ranked[0]
            second = ranked[1]
            if infer_priority(top.evidence.source_type) == infer_priority(second.evidence.source_type):
                for item in items:
                    item.status = "blocked"
                    item.needs_review = True
                blocked_fields.append(field_name)
                status = "blocked"
                db.add(
                    ConflictLog(
                        sku_id=sku_id,
                        field_name=field_name,
                        resolution="blocked",
                        chosen_candidate_id=None,
                        note="Conflict unresolved: equal reliability.",
                    )
                )
            else:
                for item in items:
                    if item.id == top.id:
                        item.status = "verified"
                        item.needs_review = False
                    else:
                        item.status = "draft"
                        item.needs_review = True
                db.add(
                    ConflictLog(
                        sku_id=sku_id,
                        field_name=field_name,
                        resolution="auto_prefer_high_reliability",
                        chosen_candidate_id=top.id,
                        note="Resolved by source priority.",
                    )
                )

    sku = db.query(SKU).filter(SKU.id == sku_id).first()
    if sku:
        if blocked_fields:
            sku.status = "blocked"
        else:
            sku.status = "verified"

    db.commit()
    return status, blocked_fields


def validate_required_fields(db: Session, sku_id: str) -> List[str]:
    missing = []
    for field_name in REQUIRED_FIELDS:
        candidate = (
            db.query(FieldCandidate)
            .filter(
                FieldCandidate.sku_id == sku_id,
                FieldCandidate.field_name == field_name,
                FieldCandidate.status == "verified",
            )
            .first()
        )
        if not candidate:
            missing.append(field_name)
    return missing
