import csv
import os
from datetime import datetime
from sqlalchemy.orm import Session
from ...models import FieldValue, ExportEvent
from ..qa.quality import validate_required_fields

REQUIRED_FIELDS = [
    "gross_weight_kg",
    "net_weight_kg",
    "carton_length_mm",
    "carton_width_mm",
    "carton_height_mm",
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
            db.query(FieldValue)
            .filter(
                FieldValue.sku_id == sku_id,
                FieldValue.field_name == field,
                FieldValue.status == "verified",
            )
            .first()
        )
        value = candidate.value
        if candidate.unit:
            value = f"{value} {candidate.unit}"
        fields[field] = value

    os.makedirs(export_dir, exist_ok=True)
    filename = f"export_{sku_id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.csv"
    path = os.path.join(export_dir, filename)
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["sku_id"] + REQUIRED_FIELDS)
        writer.writeheader()
        writer.writerow({"sku_id": sku_id, **fields})

    export_event = ExportEvent(
        sku_id=sku_id,
        export_version=1,
        change_type="data_fix",
    )
    db.add(export_event)
    db.commit()
    return path, None
