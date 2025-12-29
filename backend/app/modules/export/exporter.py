import csv
import os
from datetime import datetime
from sqlalchemy.orm import Session
from ...models import FieldCandidate, Versioning
from ..qa.quality import validate_required_fields

REQUIRED_FIELDS = [
    "gross_weight",
    "net_weight",
    "length",
    "width",
    "height",
    "capacity_wh",
    "inverter_w",
]


def generate_export(db: Session, sku_id: str, export_dir: str, exported_by: str):
    missing = validate_required_fields(db, sku_id)
    if missing:
        return None, missing

    fields = {field: None for field in REQUIRED_FIELDS}
    for field in REQUIRED_FIELDS:
        candidate = (
            db.query(FieldCandidate)
            .filter(
                FieldCandidate.sku_id == sku_id,
                FieldCandidate.field_name == field,
                FieldCandidate.status == "verified",
            )
            .first()
        )
        fields[field] = candidate.normalized_value or candidate.raw_value

    os.makedirs(export_dir, exist_ok=True)
    filename = f"export_{sku_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.csv"
    path = os.path.join(export_dir, filename)
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["sku_id"] + REQUIRED_FIELDS)
        writer.writeheader()
        writer.writerow({"sku_id": sku_id, **fields})

    version = Versioning(
        sku_id=sku_id,
        master_version=1,
        export_version=1,
        last_exported_at=datetime.utcnow(),
        exported_by=exported_by,
        change_type="data_fix",
    )
    db.add(version)
    db.commit()
    return path, None
