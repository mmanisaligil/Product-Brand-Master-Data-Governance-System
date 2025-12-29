import hashlib
from datetime import datetime
from sqlalchemy.orm import Session
from .db import SessionLocal
from .models import SKU, SKUAlias, Evidence, FieldValue, ERDecision, ConflictLog, ChangeLog


def hash_file(path: str) -> str:
    hasher = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def seed():
    db: Session = SessionLocal()
    if db.query(SKU).first():
        db.close()
        return

    sku_alpha = SKU(
        id="11111111-1111-1111-1111-111111111111",
        brand="Voltix",
        canonical_name="PowerStation Alpha 1000",
        category="Portable Power Station",
        status="verified",
    )
    sku_delta_eu = SKU(
        id="22222222-2222-2222-2222-222222222222",
        brand="EcoCharge",
        canonical_name="Delta 2 EU",
        category="Portable Power Station",
        status="draft",
    )
    sku_delta_tr = SKU(
        id="33333333-3333-3333-3333-333333333333",
        brand="EcoCharge",
        canonical_name="Delta 2 TR",
        category="Portable Power Station",
        status="draft",
    )
    sku_beta = SKU(
        id="44444444-4444-4444-4444-444444444444",
        brand="Voltix",
        canonical_name="PowerStation Beta 1500",
        category="Portable Power Station",
        status="verified",
    )
    sku_travel = SKU(
        id="55555555-5555-5555-5555-555555555555",
        brand="TravelWare",
        canonical_name="TravelPower 500",
        category="Compact Power Station",
        status="blocked",
    )
    sku_nomad = SKU(
        id="66666666-6666-6666-6666-666666666666",
        brand="Nomad",
        canonical_name="Nomad 700",
        category="Portable Power Station",
        status="draft",
    )

    db.add_all([sku_alpha, sku_delta_eu, sku_delta_tr, sku_beta, sku_travel, sku_nomad])

    db.add_all(
        [
            SKUAlias(sku_id=sku_alpha.id, alias_type="ERP_SKU", alias_value="SKU-ALPHA-1000"),
            SKUAlias(sku_id=sku_alpha.id, alias_type="EAN", alias_value="1234567890123"),
            SKUAlias(sku_id=sku_alpha.id, alias_type="SUPPLIER_CODE", alias_value="SUP-ALPHA-1000"),
            SKUAlias(sku_id=sku_alpha.id, alias_type="MODEL_NAME", alias_value="PowerStation Alpha 1000"),
            SKUAlias(sku_id=sku_delta_eu.id, alias_type="MODEL_NAME", alias_value="Delta 2 EU"),
            SKUAlias(sku_id=sku_delta_tr.id, alias_type="MODEL_NAME", alias_value="Delta 2 TR"),
            SKUAlias(sku_id=sku_beta.id, alias_type="ERP_SKU", alias_value="SKU-BETA-1500"),
            SKUAlias(sku_id=sku_travel.id, alias_type="ERP_SKU", alias_value="SKU-TRAVEL-500"),
            SKUAlias(sku_id=sku_nomad.id, alias_type="ERP_SKU", alias_value="SKU-NOMAD-700"),
        ]
    )

    evidence_alpha_path = "/data/seeds/scenario_01/evidence/ev-s01-spec.txt"
    evidence_delta_path = "/data/seeds/scenario_02/evidence/ev-s02-sheet.txt"
    evidence_beta_m_path = "/data/seeds/scenario_03/evidence/ev-s03-manufacturer.txt"
    evidence_beta_r_path = "/data/seeds/scenario_03/evidence/ev-s03-reseller.txt"
    evidence_travel_path = "/data/seeds/scenario_04/evidence/ev-s04-broker.txt"
    evidence_travel_alt_path = "/data/seeds/scenario_04/evidence/ev-s04-broker-alt.txt"
    evidence_nomad_initial_path = "/data/seeds/scenario_05/evidence/ev-s05-initial.txt"
    evidence_nomad_updated_path = "/data/seeds/scenario_05/evidence/ev-s05-updated.txt"

    evidence_alpha = Evidence(
        id="EV-S01-001",
        source_type="manufacturer_pdf",
        issuer="Voltix Labs",
        file_path=evidence_alpha_path,
        file_hash=hash_file(evidence_alpha_path),
        reliability_score=0.9,
        captured_at=datetime(2024, 1, 10),
        page_section="lines 1-6",
    )
    evidence_delta = Evidence(
        id="EV-S02-001",
        source_type="broker_doc",
        issuer="Battery Brokers",
        file_path=evidence_delta_path,
        file_hash=hash_file(evidence_delta_path),
        reliability_score=0.6,
        captured_at=datetime(2024, 2, 14),
        page_section="lines 1-8",
    )
    evidence_beta_m = Evidence(
        id="EV-S03-001",
        source_type="manufacturer_pdf",
        issuer="Voltix Labs",
        file_path=evidence_beta_m_path,
        file_hash=hash_file(evidence_beta_m_path),
        reliability_score=0.95,
        captured_at=datetime(2024, 3, 5),
        page_section="lines 1-6",
    )
    evidence_beta_r = Evidence(
        id="EV-S03-002",
        source_type="reseller",
        issuer="Reseller Hub",
        file_path=evidence_beta_r_path,
        file_hash=hash_file(evidence_beta_r_path),
        reliability_score=0.4,
        captured_at=datetime(2024, 3, 7),
        page_section="lines 1-4",
    )
    evidence_travel = Evidence(
        id="EV-S04-001",
        source_type="broker_doc",
        issuer="Global Brokers",
        file_path=evidence_travel_path,
        file_hash=hash_file(evidence_travel_path),
        reliability_score=0.5,
        captured_at=datetime(2024, 4, 12),
        page_section="lines 1-6",
    )
    evidence_travel_alt = Evidence(
        id="EV-S04-002",
        source_type="broker_doc",
        issuer="Global Brokers",
        file_path=evidence_travel_alt_path,
        file_hash=hash_file(evidence_travel_alt_path),
        reliability_score=0.5,
        captured_at=datetime(2024, 4, 13),
        page_section="lines 1-6",
    )
    evidence_nomad_initial = Evidence(
        id="EV-S05-001",
        source_type="website",
        issuer="Nomad Official",
        file_path=evidence_nomad_initial_path,
        file_hash=hash_file(evidence_nomad_initial_path),
        reliability_score=0.8,
        captured_at=datetime(2024, 4, 1),
        page_section="lines 1-6",
    )
    evidence_nomad_updated = Evidence(
        id="EV-S05-002",
        source_type="website",
        issuer="Nomad Official",
        file_path=evidence_nomad_updated_path,
        file_hash=hash_file(evidence_nomad_updated_path),
        reliability_score=0.8,
        captured_at=datetime(2024, 5, 1),
        page_section="lines 1-6",
    )

    db.add_all(
        [
            evidence_alpha,
            evidence_delta,
            evidence_beta_m,
            evidence_beta_r,
            evidence_travel,
            evidence_travel_alt,
            evidence_nomad_initial,
            evidence_nomad_updated,
        ]
    )

    db.add_all(
        [
            FieldValue(
                sku_id=sku_alpha.id,
                evidence_id=evidence_alpha.id,
                field_name="gross_weight_kg",
                value="12.500",
                unit="kg",
                confidence=0.9,
                status="verified",
            ),
            FieldValue(
                sku_id=sku_alpha.id,
                evidence_id=evidence_alpha.id,
                field_name="net_weight_kg",
                value="11.800",
                unit="kg",
                confidence=0.9,
                status="verified",
            ),
            FieldValue(
                sku_id=sku_alpha.id,
                evidence_id=evidence_alpha.id,
                field_name="carton_length_mm",
                value="400.0",
                unit="mm",
                confidence=0.9,
                status="verified",
            ),
            FieldValue(
                sku_id=sku_alpha.id,
                evidence_id=evidence_alpha.id,
                field_name="carton_width_mm",
                value="250.0",
                unit="mm",
                confidence=0.9,
                status="verified",
            ),
            FieldValue(
                sku_id=sku_alpha.id,
                evidence_id=evidence_alpha.id,
                field_name="carton_height_mm",
                value="300.0",
                unit="mm",
                confidence=0.9,
                status="verified",
            ),
            FieldValue(
                sku_id=sku_alpha.id,
                evidence_id=evidence_alpha.id,
                field_name="capacity_wh",
                value="1024",
                unit="Wh",
                confidence=0.9,
                status="verified",
            ),
            FieldValue(
                sku_id=sku_alpha.id,
                evidence_id=evidence_alpha.id,
                field_name="inverter_w",
                value="1200",
                unit="W",
                confidence=0.9,
                status="verified",
            ),
            FieldValue(
                sku_id=sku_delta_eu.id,
                evidence_id=evidence_delta.id,
                field_name="model_name",
                value="Delta 2 EU",
                unit=None,
                confidence=0.6,
                status="draft",
                needs_review=True,
            ),
            FieldValue(
                sku_id=sku_delta_tr.id,
                evidence_id=evidence_delta.id,
                field_name="model_name",
                value="Delta 2 TR",
                unit=None,
                confidence=0.6,
                status="draft",
                needs_review=True,
            ),
            FieldValue(
                sku_id=sku_delta_eu.id,
                evidence_id=evidence_delta.id,
                field_name="capacity_wh",
                value="1024",
                unit="Wh",
                confidence=0.6,
                status="draft",
                needs_review=True,
            ),
            FieldValue(
                sku_id=sku_beta.id,
                evidence_id=evidence_beta_m.id,
                field_name="gross_weight_kg",
                value="14.000",
                unit="kg",
                confidence=0.95,
                status="verified",
            ),
            FieldValue(
                sku_id=sku_beta.id,
                evidence_id=evidence_beta_r.id,
                field_name="gross_weight_kg",
                value="15.200",
                unit="kg",
                confidence=0.4,
                status="draft",
                needs_review=True,
            ),
            FieldValue(
                sku_id=sku_beta.id,
                evidence_id=evidence_beta_m.id,
                field_name="net_weight_kg",
                value="13.000",
                unit="kg",
                confidence=0.95,
                status="verified",
            ),
            FieldValue(
                sku_id=sku_beta.id,
                evidence_id=evidence_beta_m.id,
                field_name="carton_length_mm",
                value="420.0",
                unit="mm",
                confidence=0.95,
                status="verified",
            ),
            FieldValue(
                sku_id=sku_beta.id,
                evidence_id=evidence_beta_m.id,
                field_name="carton_width_mm",
                value="280.0",
                unit="mm",
                confidence=0.95,
                status="verified",
            ),
            FieldValue(
                sku_id=sku_beta.id,
                evidence_id=evidence_beta_m.id,
                field_name="carton_height_mm",
                value="310.0",
                unit="mm",
                confidence=0.95,
                status="verified",
            ),
            FieldValue(
                sku_id=sku_beta.id,
                evidence_id=evidence_beta_m.id,
                field_name="capacity_wh",
                value="1500",
                unit="Wh",
                confidence=0.95,
                status="verified",
            ),
            FieldValue(
                sku_id=sku_beta.id,
                evidence_id=evidence_beta_m.id,
                field_name="inverter_w",
                value="1800",
                unit="W",
                confidence=0.95,
                status="verified",
            ),
            FieldValue(
                sku_id=sku_travel.id,
                evidence_id=evidence_travel.id,
                field_name="net_weight_kg",
                value="7.200",
                unit="kg",
                confidence=0.5,
                status="blocked",
                needs_review=True,
            ),
            FieldValue(
                sku_id=sku_travel.id,
                evidence_id=evidence_travel_alt.id,
                field_name="net_weight_kg",
                value="6.500",
                unit="kg",
                confidence=0.5,
                status="blocked",
                needs_review=True,
            ),
            FieldValue(
                sku_id=sku_travel.id,
                evidence_id=evidence_travel.id,
                field_name="gross_weight_kg",
                value="8.000",
                unit="kg",
                confidence=0.5,
                status="verified",
            ),
            FieldValue(
                sku_id=sku_travel.id,
                evidence_id=evidence_travel.id,
                field_name="carton_length_mm",
                value="300.0",
                unit="mm",
                confidence=0.5,
                status="verified",
            ),
            FieldValue(
                sku_id=sku_travel.id,
                evidence_id=evidence_travel.id,
                field_name="carton_width_mm",
                value="200.0",
                unit="mm",
                confidence=0.5,
                status="verified",
            ),
            FieldValue(
                sku_id=sku_travel.id,
                evidence_id=evidence_travel.id,
                field_name="carton_height_mm",
                value="220.0",
                unit="mm",
                confidence=0.5,
                status="verified",
            ),
            FieldValue(
                sku_id=sku_travel.id,
                evidence_id=evidence_travel.id,
                field_name="capacity_wh",
                value="512",
                unit="Wh",
                confidence=0.5,
                status="verified",
            ),
            FieldValue(
                sku_id=sku_travel.id,
                evidence_id=evidence_travel.id,
                field_name="inverter_w",
                value="500",
                unit="W",
                confidence=0.5,
                status="verified",
            ),
            FieldValue(
                sku_id=sku_nomad.id,
                evidence_id=evidence_nomad_initial.id,
                field_name="gross_weight_kg",
                value="9.500",
                unit="kg",
                confidence=0.8,
                status="verified",
            ),
            FieldValue(
                sku_id=sku_nomad.id,
                evidence_id=evidence_nomad_initial.id,
                field_name="net_weight_kg",
                value="8.900",
                unit="kg",
                confidence=0.8,
                status="verified",
            ),
            FieldValue(
                sku_id=sku_nomad.id,
                evidence_id=evidence_nomad_initial.id,
                field_name="capacity_wh",
                value="768",
                unit="Wh",
                confidence=0.8,
                status="verified",
            ),
            FieldValue(
                sku_id=sku_nomad.id,
                evidence_id=evidence_nomad_initial.id,
                field_name="inverter_w",
                value="700",
                unit="W",
                confidence=0.8,
                status="verified",
            ),
            FieldValue(
                sku_id=sku_nomad.id,
                evidence_id=evidence_nomad_updated.id,
                field_name="carton_length_mm",
                value="360.0",
                unit="mm",
                confidence=0.8,
                status="draft",
                needs_review=True,
            ),
            FieldValue(
                sku_id=sku_nomad.id,
                evidence_id=evidence_nomad_updated.id,
                field_name="carton_width_mm",
                value="230.0",
                unit="mm",
                confidence=0.8,
                status="draft",
                needs_review=True,
            ),
            FieldValue(
                sku_id=sku_nomad.id,
                evidence_id=evidence_nomad_updated.id,
                field_name="carton_height_mm",
                value="250.0",
                unit="mm",
                confidence=0.8,
                status="draft",
                needs_review=True,
            ),
        ]
    )

    db.add_all(
        [
            ERDecision(
                sku_id=sku_delta_eu.id,
                match_score=0.45,
                match_explanation="Ambiguous model name match",
                decision_source="heuristic",
                needs_review=True,
            ),
            ERDecision(
                sku_id=sku_delta_eu.id,
                match_score=1.0,
                match_explanation="Human confirmed EU variant",
                decision_source="human_confirmed",
                needs_review=False,
                locked=True,
            ),
        ]
    )

    db.add(
        ConflictLog(
            sku_id=sku_beta.id,
            field_name="gross_weight_kg",
            resolution="auto_prefer_high_reliability",
            chosen_field_value_id=None,
            note="Manufacturer PDF preferred over reseller website.",
        )
    )
    db.add(
        ConflictLog(
            sku_id=sku_travel.id,
            field_name="net_weight_kg",
            resolution="blocked",
            chosen_field_value_id=None,
            note="Conflicting broker evidence with equal reliability.",
        )
    )

    db.add(
        ChangeLog(
            evidence_id=evidence_nomad_updated.id,
            field_name="carton_dims_mm",
            old_value="350x220x240 mm",
            new_value="360x230x250 mm",
            diff_note="Updated evidence changed carton dimensions; re-approval required.",
        )
    )

    db.commit()
    db.close()


if __name__ == "__main__":
    seed()
