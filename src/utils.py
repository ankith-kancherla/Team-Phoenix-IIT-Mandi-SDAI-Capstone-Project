"""Shared helpers for the APIPhoenix backend. Team Phoenix · Himshikhar 2026."""
from __future__ import annotations
import json, re
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "endpoints.json"

HTTP_KB = {
    400: ("Bad request", "The server could not parse the request. Check JSON syntax and required fields."),
    401: ("Unauthorized", "No valid credentials were sent. Attach a valid bearer token."),
    402: ("Payment required", "The payment step failed. Verify method and balance, then retry."),
    403: ("Forbidden", "Credentials are valid but lack permission for this resource."),
    404: ("Not found", "The resource ID or path does not exist. Verify identifiers."),
    409: ("Conflict", "The request clashes with current state (duplicate or invalid transition)."),
    422: ("Validation failed", "One or more fields failed validation. Fix types and ranges."),
    429: ("Rate limited", "Too many requests. Back off and respect Retry-After."),
    500: ("Server error", "Something failed server-side. Retry with backoff."),
    503: ("Service unavailable", "A dependency is down. Retry later."),
}


def load_endpoints() -> list[dict]:
    """Load the starter dataset shipped with the project."""
    with open(DATA_PATH) as f:
        return json.load(f)["endpoints"]


def path_params(path: str) -> list[str]:
    """Extract `{param}` names from a route path."""
    return [m[1:-1] for m in re.findall(r"\{\w+\}", path)]


def infer_type(value) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, (int, float)):
        return "number"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return "string"


def validate_endpoint(ep: dict) -> list[str]:
    """Return a list of problems with an endpoint definition (empty = valid)."""
    problems = []
    if ep.get("method", "").upper() not in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
        problems.append("method must be one of GET/POST/PUT/PATCH/DELETE")
    if not str(ep.get("path", "")).startswith("/"):
        problems.append("path must start with '/'")
    for e in ep.get("error_codes", []):
        if not isinstance(e.get("code"), int) or not (400 <= e["code"] <= 599):
            problems.append(f"error code {e.get('code')} is not a valid 4xx/5xx status")
    return problems
