import re
from typing import List, Dict
from PyPDF2 import PdfReader
import openpyxl

WEIGHT_PATTERNS = {
    "gross_weight": re.compile(r"gross\s*weight\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(kg|g|lb)", re.IGNORECASE),
    "net_weight": re.compile(r"net\s*weight\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(kg|g|lb)", re.IGNORECASE),
}

DIM_PATTERN = re.compile(
    r"dimensions\s*[:=]?\s*(\d+(?:\.\d+)?)\s*(mm|cm|m|in)\s*[x×]\s*(\d+(?:\.\d+)?)\s*(mm|cm|m|in)\s*[x×]\s*(\d+(?:\.\d+)?)\s*(mm|cm|m|in)",
    re.IGNORECASE,
)

CAPACITY_PATTERN = re.compile(r"capacity\s*[:=]?\s*(\d+(?:\.\d+)?)\s*wh", re.IGNORECASE)
INVERTER_PATTERN = re.compile(r"inverter\s*power\s*[:=]?\s*(\d+(?:\.\d+)?)\s*w", re.IGNORECASE)
MODEL_PATTERN = re.compile(r"model\s*[:=]?\s*([A-Za-z0-9\-\s]+)", re.IGNORECASE)


def extract_text_from_pdf(path: str) -> str:
    reader = PdfReader(path)
    text = "".join(page.extract_text() or "" for page in reader.pages)
    return text


def extract_text_from_xlsx(path: str) -> str:
    wb = openpyxl.load_workbook(path)
    collected = []
    for sheet in wb.worksheets:
        for row in sheet.iter_rows(values_only=True):
            for cell in row:
                if cell is not None:
                    collected.append(str(cell))
    return "\n".join(collected)


def parse_fields(text: str) -> List[Dict[str, str]]:
    candidates = []
    for key, pattern in WEIGHT_PATTERNS.items():
        match = pattern.search(text)
        if match:
            value, unit = match.groups()
            candidates.append({"field_name": key, "raw_value": f"{value} {unit}"})
    dim_match = DIM_PATTERN.search(text)
    if dim_match:
        l_val, l_unit, w_val, w_unit, h_val, h_unit = dim_match.groups()
        candidates.extend(
            [
                {"field_name": "length", "raw_value": f"{l_val} {l_unit}"},
                {"field_name": "width", "raw_value": f"{w_val} {w_unit}"},
                {"field_name": "height", "raw_value": f"{h_val} {h_unit}"},
            ]
        )
    capacity = CAPACITY_PATTERN.search(text)
    if capacity:
        candidates.append({"field_name": "capacity_wh", "raw_value": f"{capacity.group(1)} Wh"})
    inverter = INVERTER_PATTERN.search(text)
    if inverter:
        candidates.append({"field_name": "inverter_w", "raw_value": f"{inverter.group(1)} W"})
    model = MODEL_PATTERN.search(text)
    if model:
        candidates.append({"field_name": "model_name", "raw_value": model.group(1).strip()})
    return candidates


def extract_fields(path: str) -> Dict[str, List[Dict[str, str]]]:
    if path.lower().endswith(".pdf"):
        text = extract_text_from_pdf(path)
        if not text.strip():
            return {"candidates": [], "needs_review": True, "reason": "No text layer in PDF (OCR is V2)."}
    elif path.lower().endswith(".xlsx"):
        text = extract_text_from_xlsx(path)
    else:
        with open(path, "r", encoding="utf-8") as handle:
            text = handle.read()

    return {"candidates": parse_fields(text), "needs_review": False, "reason": None}
