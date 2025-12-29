from sqlalchemy.orm import Session
from typing import List, Tuple
from ...models import SKUAlias, ERDecision

STRONG_ALIAS_TYPES = {"ERP_SKU", "EAN", "SUPPLIER_CODE"}
MEDIUM_ALIAS_TYPES = {"MODEL_NAME", "CAPACITY_FINGERPRINT"}


def resolve_entities(db: Session, identifiers: List[str]) -> Tuple[str, float, str, bool, str]:
    matches = {}
    for identifier in identifiers:
        alias = db.query(SKUAlias).filter(SKUAlias.alias_value == identifier).first()
        if alias:
            matches.setdefault(alias.sku_id, []).append(alias.alias_type)

    if not matches:
        return None, 0.0, "No matching aliases found.", True, "heuristic"

    scored = []
    for sku_id, alias_types in matches.items():
        score = 0.0
        explanation_parts = []
        for alias_type in alias_types:
            if alias_type in STRONG_ALIAS_TYPES:
                score += 0.6
                explanation_parts.append(f"strong match on {alias_type}")
            elif alias_type in MEDIUM_ALIAS_TYPES:
                score += 0.3
                explanation_parts.append(f"medium match on {alias_type}")
        scored.append((sku_id, score, ", ".join(explanation_parts)))

    scored.sort(key=lambda item: item[1], reverse=True)
    if len(scored) > 1 and scored[0][1] == scored[1][1]:
        return scored[0][0], scored[0][1], "Ambiguous: " + scored[0][2], True, "heuristic"

    sku_id, score, explanation = scored[0]
    needs_review = score < 0.6
    source = "rule_based" if not needs_review else "heuristic"
    return sku_id, score, explanation, needs_review, source


def store_decision(db: Session, sku_id: str, match_score: float, explanation: str, needs_review: bool, decision_source: str) -> ERDecision:
    decision = ERDecision(
        sku_id=sku_id,
        match_score=match_score,
        match_explanation=explanation,
        needs_review=needs_review,
        decision_source=decision_source,
    )
    db.add(decision)
    db.commit()
    db.refresh(decision)
    return decision
