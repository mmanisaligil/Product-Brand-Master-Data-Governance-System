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

On container start, Alembic migrations run automatically and the seed script populates five scenarios if the database is empty.

To reset the database locally:
```bash
rm -f data/app.db
```

## Migrations + Seeds (Manual)

```bash
cd backend
alembic upgrade head
python -m app.seed
```

## Repository Layout

```
backend/               FastAPI backend
backend/migrations     Alembic migrations
backend/app/seed.py    Seed scenarios (runs on startup)
backend/app/modules    Evidence, ER, extraction, normalization, QA, export
data/seeds             Synthetic scenarios and evidence
```

## Database Connection

The app defaults to SQLite at `sqlite:////data/app.db` (via `DATABASE_URL`) and runs fully offline. The database file lives under `./data/app.db` and is persisted by the Docker volume bind.
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

### 1) List seeded SKUs
```bash
curl http://localhost:8000/api/skus
```

### 2) Upload evidence (Scenario 01)
```bash
curl -F "evidence_id=EV-S01-001" \
  -F "source_type=manufacturer_pdf" \
  -F "captured_at=2024-01-10T00:00:00" \
  -F "issuer=Voltix Labs" \
  -F "reliability_score=0.9" \
  -F "file=@data/seeds/scenario_01/evidence/ev-s01-spec.txt" \
  http://localhost:8000/api/evidence
```

### 3) Trigger extraction + normalization
```bash
curl -X POST -F "evidence_id=EV-S01-001" \
  http://localhost:8000/api/extract/11111111-1111-1111-1111-111111111111
```

### 4) Validate conflicts (Scenario 03)
```bash
curl -X POST http://localhost:8000/api/validate/44444444-4444-4444-4444-444444444444
```

### 5) Confirm ER mapping (Scenario 02)
```bash
curl -X POST http://localhost:8000/api/er/confirm/2
```

### 6) Generate ERP export
```bash
curl -X POST -F "sku_id=11111111-1111-1111-1111-111111111111" \
  -F "exported_by=demo" \
  http://localhost:8000/api/export
```

### 7) Run change detection (Scenario 05)
```bash
curl -F "evidence_id=EV-S05-002" \
  -F "source_type=website" \
  -F "captured_at=2024-05-01T00:00:00" \
  -F "issuer=Nomad Official" \
  -F "reliability_score=0.8" \
  -F "file=@data/seeds/scenario_05/evidence/ev-s05-updated.txt" \
  http://localhost:8000/api/evidence
```

## Notes

- PDF extraction reads text layers only. If no text layer exists, the system marks the evidence as `needs_review` (OCR is V2).
- Seed evidence files are stored as plain text to keep the repository diff-friendly; the extractor still supports PDF/XLSX when you upload them at runtime.
- Evidence-first model: every field candidate stores evidence linkage and confidence.
- Conflicts are stored and may block export until resolved.
