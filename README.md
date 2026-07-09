# 🔥 APIPhoenix — AI-Powered API Documentation & Testing Portal

**SDAI Himshikhar 2026 · Team Phoenix**

A portal where users enter API endpoints or upload route definitions, and the system generates human-readable documentation, ready-to-run sample requests/responses, structured test suites, and plain-English error diagnoses — so the user always knows **what to do next**.

---

## 1 · Problem statement

APIs power every modern product, but their documentation is chronically stale, hand-written, and disconnected from testing. Developers waste hours reverse-engineering endpoints, writing boilerplate sample requests, and decoding cryptic error responses. APIPhoenix takes raw route definitions as input, processes them through a clear ingest → understand → try → test → act workflow, and produces actionable output: docs a human can read, requests a human can run, tests a human can trust, and error explanations that end with a concrete next step.

## 2 · Dataset / reference source

No public dataset is required. We authored **`data/endpoints.json`** — **49 realistic endpoint records across 5 fictional services** (ShopStack e-commerce, RideLink mobility, MediTrack healthcare, EduSphere ed-tech, PayBridge fintech), following the brief's schema: `method, path, request_body, response_body, auth_required, error_codes` (plus `service`, `summary`, `tags`). The generator script is in `notebooks/generate_dataset.py` for full reproducibility.

## 3 · Tools used

| Layer | Tech |
|---|---|
| Frontend | Single-file HTML + CSS + vanilla JS, **Three.js** (3D hero) |
| Backend (optional) | **FastAPI** + **SQLite** (endpoints + generation history) |
| AI | **Claude API** (`claude-sonnet-4-6`) with a deterministic local **Phoenix engine** fallback |
| Data | Hand-authored JSON dataset, Python generator |
| Versioning | GitHub |

## 4 · Project workflow

```
endpoints.json / manual entry / upload
        │
        ▼
 Preprocess & validate  (src/preprocessing.py)
        │
        ▼
 ┌──────────────── AI layer ────────────────┐
 │ Claude API  ──fails?──▶  Phoenix engine  │   (docs · tests · error explanations)
 └───────────────────────────────────────────┘
        │
        ▼
 Portal output: Documentation · Playground · Test Lab · Error Doctor
        │
        ▼
 Export docs (.md) + pass/fail test report → user knows what to act on
```

## 5 · AI / innovation component (where and why)

1. **AI documentation generator** — Claude reads each endpoint's contract and writes structured Markdown docs (overview, parameters, responses, usage notes). *Why AI:* turning a JSON contract into readable prose is a language task, not a template task.
2. **AI test-case generator** — Claude proposes 5–7 cases per endpoint (happy path, auth, validation, not-found, business-rule edges) as strict JSON, which the portal executes in a contract-level simulated runner with a live pass/fail report.
3. **AI error explanation ("Error Doctor")** — paste any raw error → diagnosis, likely causes, and a numbered "what to do next" list.
4. **Reliability innovation** — every AI feature has a deterministic rule-based fallback (the **Phoenix engine**), so the demo and the product never break offline. The UI transparently badges which engine produced each output.

**Professional workflow features:** 📊 live **Insights dashboard** (docs/test coverage rings, method distribution, per-service progress, declared-error analysis) · **batch "Generate all docs"** with parallel AI calls and progress · **OpenAPI 3.0 export** of the entire loaded surface · **command palette** (`Ctrl+K`) with fuzzy endpoint jump · **cURL import** that parses a pasted command into the add-endpoint form · keyboard shortcuts (`/` search, `1–5` tabs).

## 6 · How to run

**Option A — portal only (zero install, zero internet):** open `app/index.html` (or `website.html` at the repo root) in any modern browser. Three.js and all fonts are **inlined**, and the 49 starter endpoints are embedded — the portal is a fully self-contained single file. AI calls run when the network allows; otherwise the Phoenix engine takes over automatically.

**Option B — full stack:**
```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...        # optional; omit to use the local engine
uvicorn app.app:app --reload               # http://127.0.0.1:8000
```

**Console demo of the engines:** `python -m src.main`

## 7 · Demo screenshots

Captured from the working prototype in `screenshots/`: `01_hero` (3D constellation), `02_docs` (generated documentation with engine badge), `03_playground` (Python sample + simulated 201), `04_testlab` (executed suite with PASS/FAIL), `05_error_doctor` (diagnosis + next steps), `06_insights` (coverage dashboard), `07_command_palette` (Ctrl+K quick find).

### Deliverables checklist

| # | Requirement | Where |
|---|---|---|
| 1 | GitHub repository | initialized with history — push per `GITHUB_SETUP.md` |
| 2 | Dataset | `data/endpoints.json` (+ `notebooks/generate_dataset.py`) |
| 3 | Code files / notebooks | `app/`, `src/`, `notebooks/exploration.ipynb` (executed) |
| 4 | README | this file |
| 5 | Project documentation/report | `docs/project_report.md` |
| 6 | Presentation PPT/PDF | `docs/presentation.pptx` + `.pdf` |
| 7 | Demo video | record using `docs/demo_video_script.md` (manual step) |
| 8 | Requirements file | `requirements.txt` |
| 9 | Screenshots of working prototype | `screenshots/*.png` |
| 10 | Limitations & responsible use | §9–10 below, report §7, deck slide 8 |

## 8 · Results and insights

- 49/49 starter endpoints produce complete documentation via either engine.
- The simulated Test Lab derives its expected statuses from the endpoint contract itself, giving an honest validation method: a test only passes if the contract actually declares the behavior.
- Fallback design insight: pairing an LLM with a deterministic engine converts "AI demo risk" into a graceful-degradation story — output quality drops, availability doesn't.

## 9 · Limitations

- Test execution is **contract-level simulation**, not live HTTP against a deployed server (starter services are fictional).
- AI output can be imprecise; the engine badge lets users judge provenance, but generated docs should be reviewed before publishing.
- The single-file portal keeps state in memory; the FastAPI + SQLite path persists it.

## 10 · Responsible use

- Never paste secrets/tokens/PHI into definitions or the Error Doctor; sample data is fully fictional.
- AI-generated documentation and tests are assistive drafts — a human must review before production use.
- Rate-limit and attribution: AI calls are minimal (one per generation click) and outputs are labeled by engine.

## 11 · Future improvements

Live test execution against real base URLs with CORS-aware proxying · OpenAPI/Swagger import & export · versioned doc diffs · CI hook that fails builds when contracts drift from docs.

## 12 · Team

**Team Phoenix** — Sri Varshith Vaitla · Nekkanti Bhavita · Pula Nikarika · Sai Ankith Reddy Kancherla
