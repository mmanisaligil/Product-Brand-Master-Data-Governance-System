# Product & Brand Master Data Governance System (V1)

Offline-first, evidence-driven prototype for governing product and brand master data with field-level traceability, explicit uncertainty, human confirmation, and deterministic ERP exports.

## Quick Start

```bash
cp .env.example .env
docker compose up --build
```

* API: http://localhost:8000
* UI: http://localhost:8000/
* Health check: `GET /health`

## Repository Layout

```
backend/               FastAPI backend
backend/db/init.sql    Schema + seed data
backend/app/modules    Evidence, ER, extraction, normalization, QA, export
data/seeds             Synthetic scenarios and evidence
```

## Seeded Demo Scenarios

Each scenario ships with:
- seeded DB records
- evidence files in `data/seeds/scenario_X/evidence/`
- expected ERP CSV when export is allowed

1. **Scenario 01 — Clean happy path**
2. **Scenario 02 — Ambiguous ER requires human_confirmed**
3. **Scenario 03 — Field conflict resolved by rule preference**
4. **Scenario 04 — Conflict remains and blocks export**
5. **Scenario 05 — Change detection + selective invalidation**

## Demo Walkthrough (Curl)

### 1) Upload evidence (Scenario 01)
```bash
curl -F "evidence_id=EV-S01-001" \
  -F "source_type=manufacturer_datasheet" \
  -F "capture_date=2024-01-10T00:00:00" \
  -F "issuer=Alpha Energy" \
  -F "reliability_score=0.9" \
  -F "scope=SKU-ALPHA-1000" \
  -F "file=@data/seeds/scenario_01/evidence/ev-s01-spec.txt" \
  http://localhost:8000/evidence/upload
```

### 2) Trigger extraction + normalization
```bash
curl -X POST http://localhost:8000/extraction/run/EV-S01-001
```

### 3) View SKU status + field mappings
```bash
curl http://localhost:8000/skus
curl http://localhost:8000/fields/SKU-ALPHA-1000
```

### 4) Resolve conflict (Scenario 03)
```bash
curl -X POST http://localhost:8000/qa/resolve/SKU-BETA-1500
```

### 5) Confirm ER mapping (Scenario 02)
```bash
curl -X POST http://localhost:8000/er/confirm/2
```

### 6) Generate ERP export
```bash
curl -X POST -F "exported_by=demo" http://localhost:8000/export/SKU-ALPHA-1000
```

### 7) Run change detection (Scenario 05)
```bash
curl -F "evidence_id=EV-S05-001" \
  -F "source_type=official_update" \
  -F "capture_date=2024-05-01T00:00:00" \
  -F "issuer=Nomad Official" \
  -F "reliability_score=0.8" \
  -F "scope=SKU-NOMAD-700" \
  -F "file=@data/seeds/scenario_05/evidence/ev-s05-updated.txt" \
  http://localhost:8000/evidence/upload
```

## Notes

- PDF extraction reads text layers only. If no text layer exists, the system marks the evidence as `needs_review` (OCR is V2).
- Seed evidence files are stored as plain text to keep the repository diff-friendly; the extractor still supports PDF/XLSX when you upload them at runtime.
- Evidence-first model: every field candidate stores evidence linkage and confidence.
- Conflicts are stored and may block export until resolved.
