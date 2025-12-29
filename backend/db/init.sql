CREATE TABLE evidence (
    id TEXT PRIMARY KEY,
    source_type TEXT NOT NULL,
    file_hash TEXT NOT NULL,
    capture_date TIMESTAMP NOT NULL,
    issuer TEXT NOT NULL,
    scope TEXT,
    page_section TEXT,
    reliability_score FLOAT NOT NULL,
    file_path TEXT NOT NULL
);

CREATE TABLE skus (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft'
);

CREATE TABLE sku_aliases (
    id SERIAL PRIMARY KEY,
    sku_id TEXT NOT NULL REFERENCES skus(id),
    alias_type TEXT NOT NULL,
    alias_value TEXT NOT NULL
);

CREATE TABLE er_decisions (
    id SERIAL PRIMARY KEY,
    evidence_id TEXT NOT NULL REFERENCES evidence(id),
    sku_id TEXT NOT NULL REFERENCES skus(id),
    match_score FLOAT NOT NULL,
    match_explanation TEXT NOT NULL,
    needs_review BOOLEAN DEFAULT FALSE,
    decision_source TEXT NOT NULL,
    locked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE field_candidates (
    id SERIAL PRIMARY KEY,
    sku_id TEXT NOT NULL REFERENCES skus(id),
    evidence_id TEXT NOT NULL REFERENCES evidence(id),
    field_name TEXT NOT NULL,
    raw_value TEXT NOT NULL,
    normalized_value TEXT,
    confidence FLOAT NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft',
    needs_review BOOLEAN DEFAULT FALSE
);

CREATE TABLE conflict_logs (
    id SERIAL PRIMARY KEY,
    sku_id TEXT NOT NULL REFERENCES skus(id),
    field_name TEXT NOT NULL,
    resolution TEXT NOT NULL,
    chosen_candidate_id INTEGER REFERENCES field_candidates(id),
    note TEXT,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE change_logs (
    id SERIAL PRIMARY KEY,
    evidence_id TEXT NOT NULL REFERENCES evidence(id),
    field_name TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    diff_note TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE versioning (
    id SERIAL PRIMARY KEY,
    sku_id TEXT NOT NULL REFERENCES skus(id),
    master_version INTEGER NOT NULL,
    export_version INTEGER NOT NULL,
    last_exported_at TIMESTAMP,
    exported_by TEXT,
    change_type TEXT NOT NULL
);

INSERT INTO skus (id, name, status) VALUES
('SKU-ALPHA-1000', 'PowerStation Alpha 1000', 'verified'),
('SKU-DELTA-2-EU', 'Delta 2 EU', 'draft'),
('SKU-DELTA-2-TR', 'Delta 2 TR', 'draft'),
('SKU-BETA-1500', 'PowerStation Beta 1500', 'verified'),
('SKU-TRAVEL-500', 'TravelPower 500', 'blocked'),
('SKU-NOMAD-700', 'Nomad 700', 'draft');

INSERT INTO sku_aliases (sku_id, alias_type, alias_value) VALUES
('SKU-ALPHA-1000', 'sku', 'ALPHA-1000'),
('SKU-ALPHA-1000', 'ean', '1234567890123'),
('SKU-ALPHA-1000', 'supplier_code', 'SUP-ALPHA-1000'),
('SKU-DELTA-2-EU', 'model_name', 'Delta 2 EU'),
('SKU-DELTA-2-TR', 'model_name', 'Delta 2 TR'),
('SKU-BETA-1500', 'sku', 'BETA-1500'),
('SKU-TRAVEL-500', 'sku', 'TRAVEL-500'),
('SKU-NOMAD-700', 'sku', 'NOMAD-700');

INSERT INTO evidence (id, source_type, file_hash, capture_date, issuer, scope, page_section, reliability_score, file_path) VALUES
('EV-S01-001', 'manufacturer_datasheet', '3a427e4a4e7fc51f9c83e29027b43775f7c013f026f0eebf0f2b4d6aa734bd7c', '2024-01-10', 'Alpha Energy', 'SKU-ALPHA-1000', 'lines 1-6', 0.9, '/data/seeds/scenario_01/evidence/ev-s01-spec.txt'),
('EV-S02-001', 'broker_sheet', 'dfb20b20e05b17ab430882291fce8bc3647bee6f52b89388d1437838ec39e021', '2024-02-14', 'Battery Brokers', NULL, 'Sheet Specs', 0.6, '/data/seeds/scenario_02/evidence/ev-s02-sheet.txt'),
('EV-S03-001', 'manufacturer_signed_pdf', '2b7822f708012c2d6f7a7150f9c7bb4db39e32650b3d0a4cb1b1da3db8349b66', '2024-03-05', 'Beta Power', 'SKU-BETA-1500', 'page 1', 0.95, '/data/seeds/scenario_03/evidence/ev-s03-manufacturer.txt'),
('EV-S03-002', 'reseller_web_text', '469425d8a484fcbda6ac72eb7b617b6792349c83e5f8cfcd4576ae6e928a09e5', '2024-03-07', 'Reseller Hub', 'SKU-BETA-1500', 'lines 1-4', 0.4, '/data/seeds/scenario_03/evidence/ev-s03-reseller.txt'),
('EV-S04-001', 'broker_text', '7a671c81c3babfc2d51988d32e320b07b260a2db62bf3bb557e2b3ac895b1699', '2024-04-12', 'Global Brokers', 'SKU-TRAVEL-500', 'lines 1-6', 0.5, '/data/seeds/scenario_04/evidence/ev-s04-broker.txt'),
('EV-S04-002', 'broker_text', '184609cbb5e0cabdc334b4faf01cbc021d932edf3fca41e3189110ce9cfb80aa', '2024-04-13', 'Global Brokers', 'SKU-TRAVEL-500', 'lines 1-6', 0.5, '/data/seeds/scenario_04/evidence/ev-s04-broker-alt.txt'),
('EV-S05-001', 'official_update', '3dbdc69121ed76528bf842b14c788127895e341ee5892f76b27cd0ea16823a1f', '2024-05-01', 'Nomad Official', 'SKU-NOMAD-700', 'lines 1-6', 0.8, '/data/seeds/scenario_05/evidence/ev-s05-updated.txt'),
('EV-S05-002', 'official_sheet', 'e64962629d61e2e03d27a31d46324327dede946a0f6a0803db886f6616bff81b', '2024-04-01', 'Nomad Official', 'SKU-NOMAD-700', 'lines 1-6', 0.8, '/data/seeds/scenario_05/evidence/ev-s05-initial.txt');

INSERT INTO field_candidates (sku_id, evidence_id, field_name, raw_value, normalized_value, confidence, status, needs_review) VALUES
('SKU-ALPHA-1000', 'EV-S01-001', 'gross_weight', '12.5 kg', '12.500 kg', 0.9, 'verified', FALSE),
('SKU-ALPHA-1000', 'EV-S01-001', 'net_weight', '11.8 kg', '11.800 kg', 0.9, 'verified', FALSE),
('SKU-ALPHA-1000', 'EV-S01-001', 'length', '400 mm', '400.0 mm', 0.9, 'verified', FALSE),
('SKU-ALPHA-1000', 'EV-S01-001', 'width', '250 mm', '250.0 mm', 0.9, 'verified', FALSE),
('SKU-ALPHA-1000', 'EV-S01-001', 'height', '300 mm', '300.0 mm', 0.9, 'verified', FALSE),
('SKU-ALPHA-1000', 'EV-S01-001', 'capacity_wh', '1024 Wh', '1024 Wh', 0.9, 'verified', FALSE),
('SKU-ALPHA-1000', 'EV-S01-001', 'inverter_w', '1200 W', '1200 W', 0.9, 'verified', FALSE),
('SKU-ALPHA-1000', 'EV-S01-001', 'model_name', 'PowerStation Alpha 1000', 'PowerStation Alpha 1000', 0.9, 'verified', FALSE),

('SKU-DELTA-2-EU', 'EV-S02-001', 'model_name', 'Delta 2 EU', 'Delta 2 EU', 0.6, 'draft', TRUE),
('SKU-DELTA-2-EU', 'EV-S02-001', 'capacity_wh', '1024 Wh', '1024 Wh', 0.6, 'draft', TRUE),

('SKU-BETA-1500', 'EV-S03-001', 'gross_weight', '14.0 kg', '14.000 kg', 0.95, 'verified', FALSE),
('SKU-BETA-1500', 'EV-S03-001', 'net_weight', '13.0 kg', '13.000 kg', 0.95, 'verified', FALSE),
('SKU-BETA-1500', 'EV-S03-001', 'length', '420 mm', '420.0 mm', 0.95, 'verified', FALSE),
('SKU-BETA-1500', 'EV-S03-001', 'width', '280 mm', '280.0 mm', 0.95, 'verified', FALSE),
('SKU-BETA-1500', 'EV-S03-001', 'height', '310 mm', '310.0 mm', 0.95, 'verified', FALSE),
('SKU-BETA-1500', 'EV-S03-001', 'capacity_wh', '1500 Wh', '1500 Wh', 0.95, 'verified', FALSE),
('SKU-BETA-1500', 'EV-S03-001', 'inverter_w', '1800 W', '1800 W', 0.95, 'verified', FALSE),
('SKU-BETA-1500', 'EV-S03-002', 'gross_weight', '15.2 kg', '15.200 kg', 0.4, 'draft', TRUE),

('SKU-TRAVEL-500', 'EV-S04-001', 'gross_weight', '8.0 kg', '8.000 kg', 0.5, 'verified', FALSE),
('SKU-TRAVEL-500', 'EV-S04-001', 'net_weight', '7.2 kg', '7.200 kg', 0.5, 'blocked', TRUE),
('SKU-TRAVEL-500', 'EV-S04-001', 'length', '300 mm', '300.0 mm', 0.5, 'verified', FALSE),
('SKU-TRAVEL-500', 'EV-S04-001', 'width', '200 mm', '200.0 mm', 0.5, 'verified', FALSE),
('SKU-TRAVEL-500', 'EV-S04-001', 'height', '220 mm', '220.0 mm', 0.5, 'verified', FALSE),
('SKU-TRAVEL-500', 'EV-S04-001', 'capacity_wh', '512 Wh', '512 Wh', 0.5, 'verified', FALSE),
('SKU-TRAVEL-500', 'EV-S04-001', 'inverter_w', '500 W', '500 W', 0.5, 'verified', FALSE),
('SKU-TRAVEL-500', 'EV-S04-002', 'net_weight', '6.5 kg', '6.500 kg', 0.5, 'blocked', TRUE),

('SKU-NOMAD-700', 'EV-S05-001', 'length', '360 mm', '360.0 mm', 0.8, 'draft', TRUE),
('SKU-NOMAD-700', 'EV-S05-001', 'width', '230 mm', '230.0 mm', 0.8, 'draft', TRUE),
('SKU-NOMAD-700', 'EV-S05-001', 'height', '250 mm', '250.0 mm', 0.8, 'draft', TRUE),
('SKU-NOMAD-700', 'EV-S05-002', 'gross_weight', '9.5 kg', '9.500 kg', 0.8, 'verified', FALSE),
('SKU-NOMAD-700', 'EV-S05-002', 'net_weight', '8.9 kg', '8.900 kg', 0.8, 'verified', FALSE),
('SKU-NOMAD-700', 'EV-S05-002', 'capacity_wh', '768 Wh', '768 Wh', 0.8, 'verified', FALSE),
('SKU-NOMAD-700', 'EV-S05-002', 'inverter_w', '700 W', '700 W', 0.8, 'verified', FALSE);

INSERT INTO er_decisions (evidence_id, sku_id, match_score, match_explanation, needs_review, decision_source, locked) VALUES
('EV-S02-001', 'SKU-DELTA-2-EU', 0.45, 'Ambiguous model name match', TRUE, 'heuristic', FALSE),
('EV-S02-001', 'SKU-DELTA-2-EU', 1.0, 'Human confirmed EU variant', FALSE, 'human_confirmed', TRUE);

INSERT INTO conflict_logs (sku_id, field_name, resolution, chosen_candidate_id, note) VALUES
('SKU-BETA-1500', 'gross_weight', 'auto_prefer_high_reliability', 11, 'Manufacturer PDF preferred over reseller text.'),
('SKU-TRAVEL-500', 'net_weight', 'blocked', NULL, 'Conflicting broker evidence with equal reliability.');

INSERT INTO change_logs (evidence_id, field_name, old_value, new_value, diff_note) VALUES
('EV-S05-001', 'dimensions', '350x220x240 mm', '360x230x250 mm', 'Updated evidence changed carton dimensions; re-approval required.');

INSERT INTO versioning (sku_id, master_version, export_version, last_exported_at, exported_by, change_type) VALUES
('SKU-ALPHA-1000', 1, 1, '2024-01-12', 'seed', 'data_fix'),
('SKU-BETA-1500', 1, 1, '2024-03-08', 'seed', 'data_fix');
