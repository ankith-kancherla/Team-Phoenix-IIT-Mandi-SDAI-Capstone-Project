"""Normalize raw/uploaded route definitions into the portal's canonical schema.

Accepts either a bare list of endpoints or {"endpoints": [...]}. Fills missing
fields with safe defaults and drops records that fail validation.
"""
from __future__ import annotations
import json
from .utils import validate_endpoint

CANONICAL_FIELDS = ("id", "service", "method", "path", "summary",
                    "auth_required", "request_body", "response_body",
                    "error_codes", "tags")


def normalize_record(raw: dict, index: int) -> dict:
    return {
        "id": raw.get("id") or f"up_{index:03d}",
        "service": raw.get("service") or "Imported",
        "method": str(raw.get("method", "GET")).upper(),
        "path": raw.get("path") or "/",
        "summary": raw.get("summary") or "Imported endpoint",
        "auth_required": bool(raw.get("auth_required", False)),
        "request_body": raw.get("request_body"),
        "response_body": raw.get("response_body") or {},
        "error_codes": raw.get("error_codes") or [],
        "tags": raw.get("tags") or [],
    }


def preprocess(payload: str | bytes | dict | list) -> tuple[list[dict], list[str]]:
    """Return (clean_endpoints, warnings)."""
    if isinstance(payload, (str, bytes)):
        payload = json.loads(payload)
    records = payload.get("endpoints", []) if isinstance(payload, dict) else payload
    clean, warnings = [], []
    for i, raw in enumerate(records):
        rec = normalize_record(raw, i)
        problems = validate_endpoint(rec)
        if problems:
            warnings.append(f"{rec['method']} {rec['path']}: dropped ({'; '.join(problems)})")
            continue
        clean.append(rec)
    return clean, warnings
