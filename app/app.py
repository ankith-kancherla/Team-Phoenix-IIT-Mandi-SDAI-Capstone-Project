"""FastAPI backend for APIPhoenix (optional — the portal in index.html is
fully self-contained; this exposes the same engines as REST + serves the UI).

Run:  uvicorn app.app:app --reload   →  http://127.0.0.1:8000
"""
from __future__ import annotations
import sqlite3, json
from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile
from fastapi.responses import FileResponse
from src.main import generate_docs, generate_tests, run_suite, explain_error
from src.preprocessing import preprocess
from src.utils import load_endpoints

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "portal.db"

app = FastAPI(title="APIPhoenix API", version="1.0",
              description="AI-Powered API Documentation & Testing Portal — Team Phoenix")


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB)
    conn.execute("""CREATE TABLE IF NOT EXISTS endpoints(
        id TEXT PRIMARY KEY, payload TEXT NOT NULL)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS generations(
        id INTEGER PRIMARY KEY AUTOINCREMENT, endpoint_id TEXT,
        kind TEXT, engine TEXT, output TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""")
    return conn


@app.on_event("startup")
def seed():
    conn = db()
    if conn.execute("SELECT COUNT(*) FROM endpoints").fetchone()[0] == 0:
        for ep in load_endpoints():
            conn.execute("INSERT INTO endpoints VALUES(?,?)", (ep["id"], json.dumps(ep)))
        conn.commit()
    conn.close()


def get_ep(endpoint_id: str) -> dict:
    row = db().execute("SELECT payload FROM endpoints WHERE id=?", (endpoint_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Endpoint not found")
    return json.loads(row[0])


@app.get("/")
def ui():
    return FileResponse(ROOT / "app" / "index.html")


@app.get("/api/endpoints")
def list_endpoints():
    rows = db().execute("SELECT payload FROM endpoints").fetchall()
    return {"count": len(rows), "endpoints": [json.loads(r[0]) for r in rows]}


@app.post("/api/endpoints/upload")
async def upload(file: UploadFile):
    clean, warnings = preprocess(await file.read())
    conn = db()
    for ep in clean:
        conn.execute("INSERT OR REPLACE INTO endpoints VALUES(?,?)", (ep["id"], json.dumps(ep)))
    conn.commit()
    return {"imported": len(clean), "warnings": warnings}


@app.post("/api/endpoints/{endpoint_id}/docs")
def docs(endpoint_id: str):
    ep = get_ep(endpoint_id)
    out = generate_docs(ep)
    conn = db()
    conn.execute("INSERT INTO generations(endpoint_id,kind,engine,output) VALUES(?,?,?,?)",
                 (endpoint_id, "docs", out["engine"], out["markdown"]))
    conn.commit()
    return out


@app.post("/api/endpoints/{endpoint_id}/tests")
def tests(endpoint_id: str):
    ep = get_ep(endpoint_id)
    suite = generate_tests(ep)
    results = run_suite(ep, suite["cases"])
    conn = db()
    conn.execute("INSERT INTO generations(endpoint_id,kind,engine,output) VALUES(?,?,?,?)",
                 (endpoint_id, "tests", suite["engine"], json.dumps(results)))
    conn.commit()
    return {"engine": suite["engine"], "results": results,
            "passed": sum(r["result"] == "pass" for r in results), "total": len(results)}


@app.post("/api/explain-error")
def explain(payload: dict):
    return explain_error(payload.get("error", ""), payload.get("endpoint"))
