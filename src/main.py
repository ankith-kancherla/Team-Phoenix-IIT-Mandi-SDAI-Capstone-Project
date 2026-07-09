"""APIPhoenix core engines — documentation, test-case generation, error explanation.

Two layers:
  1. Claude AI (if ANTHROPIC_API_KEY is set) for rich natural-language output.
  2. A deterministic local "Phoenix engine" fallback so the pipeline never breaks
     offline — the same logic that ships inside app/index.html.

Run a quick demo:  python -m src.main
"""
from __future__ import annotations
import json, os
from .utils import HTTP_KB, load_endpoints, path_params, infer_type

# ── optional AI layer ────────────────────────────────────────────────
def ask_claude(prompt: str, system: str = "You are an expert API technical writer.") -> str | None:
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return None
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=key)
        msg = client.messages.create(
            model="claude-sonnet-4-6", max_tokens=1000,
            system=system, messages=[{"role": "user", "content": prompt}],
        )
        return "".join(b.text for b in msg.content if b.type == "text")
    except Exception:
        return None


# ── documentation generator ─────────────────────────────────────────
def generate_docs(ep: dict) -> dict:
    ai = ask_claude(
        "Write concise developer documentation in Markdown (### Overview, "
        "Path parameters, Request fields, Success response, Error handling, "
        f"Usage note) for this REST endpoint:\n{json.dumps(ep, indent=2)}"
    )
    if ai:
        return {"engine": "claude", "markdown": ai}

    lines = [f"### Overview\n{ep['summary']}. `{ep['method']}` endpoint of the "
             f"**{ep['service']}** service"
             + (" — requires a bearer token." if ep["auth_required"] else " — public.")]
    if (params := path_params(ep["path"])):
        lines.append("### Path parameters\n" + "\n".join(f"- `{p}` — required identifier" for p in params))
    body = ep.get("request_body")
    if body and "query" not in (body or {}):
        lines.append("### Request fields\n" + "\n".join(
            f"- `{k}` ({infer_type(v)})" for k, v in body.items()))
    lines.append("### Success response\nReturns fields: "
                 + ", ".join(f"`{k}`" for k in (ep.get("response_body") or {})))
    lines.append("### Error handling\n" + "\n".join(
        f"- `{e['code']}` — {e['message']}" for e in ep.get("error_codes", [])))
    return {"engine": "phoenix", "markdown": "\n\n".join(lines)}


# ── test-case generator ──────────────────────────────────────────────
def generate_tests(ep: dict) -> dict:
    ai = ask_claude(
        "Generate 5-7 JSON test cases for this endpoint. Respond ONLY with a JSON array "
        'of {"name","type","detail","expect"}:\n' + json.dumps(ep, indent=2),
        system="You are a QA engineer. Output strictly valid JSON only.")
    if ai:
        try:
            return {"engine": "claude", "cases": json.loads(ai.replace("```json", "").replace("```", ""))}
        except json.JSONDecodeError:
            pass

    cases = [{"name": "Happy path returns success", "type": "positive",
              "detail": f"Valid {ep['method']} to {ep['path']} with the documented body.",
              "expect": "2xx"}]
    if ep["auth_required"]:
        cases.append({"name": "Rejects missing bearer token", "type": "auth",
                      "detail": "Repeat without the Authorization header.", "expect": "401"})
    if ep.get("request_body") and "query" not in ep["request_body"]:
        cases.append({"name": "Rejects malformed body", "type": "validation",
                      "detail": "Remove a required field or send a wrong type.", "expect": "422"})
    if path_params(ep["path"]):
        cases.append({"name": "Unknown ID returns 404", "type": "negative",
                      "detail": "Use a non-existent path parameter value.", "expect": "404"})
    cases.append({"name": "Wrong method returns 405", "type": "contract",
                  "detail": "Call the path with a different HTTP method.", "expect": "405"})
    return {"engine": "phoenix", "cases": cases}


def run_suite(ep: dict, cases: list[dict]) -> list[dict]:
    """Contract-level simulated runner (no live server needed for the demo)."""
    results = []
    for t in cases:
        exp = str(t.get("expect", ""))
        ok = (exp == "2xx"
              or (exp == "401" and ep["auth_required"])
              or (exp == "422" and bool(ep.get("request_body")))
              or (exp == "404" and bool(path_params(ep["path"])))
              or exp == "405"
              or any(str(e["code"]) == exp for e in ep.get("error_codes", [])))
        results.append({**t, "result": "pass" if ok else "fail"})
    return results


# ── error explanation ────────────────────────────────────────────────
def explain_error(raw: str, ep: dict | None = None) -> dict:
    ai = ask_claude(
        "Explain this API error (### Diagnosis / Likely causes / What to do next):\n"
        + raw + ("\nEndpoint: " + json.dumps(ep) if ep else ""))
    if ai:
        return {"engine": "claude", "markdown": ai}
    import re
    code = next((int(m) for m in re.findall(r"\b([45]\d\d)\b", raw)), None)
    title, hint = HTTP_KB.get(code, ("Application error", "No standard HTTP status detected."))
    return {"engine": "phoenix", "markdown":
            f"### Diagnosis\nHTTP {code or '?'} — **{title}**. {hint}\n\n"
            "### What to do next\n1. Reproduce with the Playground sample request.\n"
            "2. Compare input against the documented schema.\n"
            "3. Attach the request ID to a bug report if it persists."}


if __name__ == "__main__":
    eps = load_endpoints()
    ep = eps[0]
    print(f"Loaded {len(eps)} endpoints. Demo on: {ep['method']} {ep['path']}\n")
    docs = generate_docs(ep)
    print(f"[docs · {docs['engine']}]\n{docs['markdown'][:400]}…\n")
    suite = generate_tests(ep)
    results = run_suite(ep, suite["cases"])
    passed = sum(r["result"] == "pass" for r in results)
    print(f"[tests · {suite['engine']}] {passed}/{len(results)} passed")
    for r in results:
        print(f"  {r['result'].upper():4} · {r['name']} (expect {r['expect']})")
    err = explain_error('{"error":{"code":422,"message":"Validation failed"}}', ep)
    print(f"\n[error doctor · {err['engine']}]\n{err['markdown'][:300]}…")
