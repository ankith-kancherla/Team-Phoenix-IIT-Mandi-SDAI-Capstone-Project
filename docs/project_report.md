# APIPhoenix — Project Report
**AI-Powered API Documentation & Testing Portal · SDAI Himshikhar 2026 · Team Phoenix**
Sri Varshith Vaitla · Nekkanti Bhavita · Pula Nikarika · Sai Ankith Reddy Kancherla

---

## 1. Problem statement and real-world impact

Every software team consumes and publishes APIs, yet documentation is the first thing to rot. Studies of developer workflow consistently show engineers spending a large share of integration time reading, guessing at, or reverse-engineering endpoint behavior. The pain is threefold: (a) docs are hand-written and drift from the code, (b) sample requests must be assembled by hand for every language, and (c) error responses arrive as cryptic JSON with no guidance.

APIPhoenix attacks all three with one workflow. A user provides route definitions (upload, manual entry, or bundled starter data). The system generates documentation, sample requests/responses, and test cases — and, critically, does not stop at code execution: the Error Doctor and pass/fail test report end every interaction with a concrete next action for the user ("refresh the token and confirm the Authorization header", "compare field X against the schema", "3/6 tests failed — the contract does not declare 429").

**Users:** student teams shipping hackathon backends, junior developers onboarding onto unfamiliar APIs, and small startups without dedicated docs engineers.

## 2. Data

Per the brief, we authored starter data rather than using a public dataset. `data/endpoints.json` contains **49 records across 5 fictional but realistic services**:

| Service | Domain | Endpoints |
|---|---|---|
| ShopStack | e-commerce (auth, catalog, cart, orders, payments, reviews) | 16 |
| RideLink | mobility (estimates, rides, drivers, surge, wallet) | 10 |
| MediTrack | healthcare (patients, appointments, prescriptions, labs, vitals) | 9 |
| EduSphere | ed-tech (courses, enrollments, quizzes, certificates) | 7 |
| PayBridge | fintech (intents, capture, refunds, settlements, webhooks, UPI) | 7 |

Each record follows the required schema — `method, path, request_body, response_body, auth_required, error_codes` — enriched with `service`, `summary`, and `tags`. Records deliberately vary: public vs. authenticated routes, query-parameter vs. body-parameter requests, path parameters, and domain-specific business errors (402 payment failures, 409 stock conflicts, 423 locked lab reports, 429 rate limits). The generator (`notebooks/generate_dataset.py`) makes the dataset reproducible and extensible.

## 3. System architecture and workflow

```
                ┌────────────────────────────────────────────┐
 Input layer    │ upload endpoints.json · add-endpoint form  │
                │ · 49 bundled starter endpoints             │
                └──────────────────┬─────────────────────────┘
                                   ▼
 Processing     preprocessing.py → normalize, validate, drop bad records
                                   ▼
                ┌───────────── AI layer ─────────────┐
                │  Claude API (claude-sonnet-4-6)    │
                │        │  on failure/offline       │
                │        ▼                           │
                │  Phoenix local rule engine         │
                └──────────────────┬─────────────────┘
                                   ▼
 Output layer   Documentation tab · Playground (cURL/JS/Python samples,
                simulated responses) · Test Lab (suite + runner + report)
                · Error Doctor (diagnosis + next steps) · Markdown export
                                   ▼
 Persistence    SQLite (endpoints, generation history)  [FastAPI path]
```

The portal itself is a **single self-contained HTML file** (`app/index.html`) — vanilla JS, Three.js for the 3D hero, no build step — deployable anywhere. An optional **FastAPI backend** (`app/app.py`) exposes the same engines as REST (`/api/endpoints`, `/api/endpoints/{id}/docs`, `/api/endpoints/{id}/tests`, `/api/explain-error`) and persists to SQLite, satisfying the frontend/backend/database structure criterion.

## 4. AI component — where and why

**Where:** three generation tasks call Claude (`claude-sonnet-4-6`): documentation writing (JSON contract → structured Markdown prose), test-suite design (contract → strict-JSON array of 5–7 cases spanning positive/auth/validation/negative/edge/contract types), and error explanation (raw error text + endpoint context → diagnosis and numbered next steps).

**Why AI is genuinely useful here:** translating a machine contract into prose a human can act on is a language problem. Templates can list fields; they cannot explain that a PUT is an idempotent full replacement, or infer that a 409 on `/cart/items` probably means a stock race, or read an arbitrary pasted stack trace. The LLM supplies judgment and language; the system supplies structure and verification.

**Engineering innovation — the Phoenix fallback engine:** every AI call is wrapped so that failure (offline, quota, malformed output) silently falls through to a deterministic rule engine implementing the same three tasks from the endpoint schema and an HTTP-status knowledge base. The UI badges each output "⚡ Claude AI" or "🛠 Phoenix local engine," making provenance transparent. This design converts LLM availability risk into graceful degradation.

## 5. Evaluation / validation method

- **Contract-grounded test runner:** the Test Lab does not rubber-stamp results. Each generated case declares an expected status; the runner passes it only if the endpoint's own contract supports that behavior (e.g., a 401 case passes only when `auth_required` is true; a 429 case only when the contract lists 429). AI-generated suites are therefore validated against ground truth from the dataset.
- **Coverage check:** all 49 starter endpoints produce complete docs and ≥3-case suites through the fallback engine alone (verified via `python -m src.main` and batch runs), guaranteeing a floor of quality independent of the AI.
- **Input validation:** uploads pass through `preprocessing.py`, which normalizes records and reports dropped/invalid ones as warnings rather than failing silently.

## 6. Results

- 49/49 endpoints documented; 5 services; 6 test-case archetypes; 3 sample-request languages (cURL, JavaScript, Python).
- Simulated suite runs report per-case PASS/FAIL with an animated progress bar and a summary toast (e.g., "5/6 passed"), plus one-click hand-off of any simulated failure into the Error Doctor.
- Markdown export bundles every generated doc into a single shareable `apiphoenix-docs.md`.

## 7. Limitations and responsible use

1. Test execution is simulation at the contract level; live HTTP execution against arbitrary user servers is future work (needs CORS-aware proxying and auth handling).
2. LLM output can be wrong or over-confident; the engine badge and the contract-grounded runner mitigate but do not eliminate this. Generated docs are drafts requiring human review.
3. Users must not paste secrets, tokens, or personal/health data into definitions or the Error Doctor. All bundled data is fictional.
4. AI usage is minimal and user-initiated (one call per explicit generation click) — no background calls.

## 8. Future improvements

Live test execution mode · OpenAPI 3.1 import/export · doc-drift detection in CI · multi-user workspaces on the FastAPI/SQLite path · response-schema assertion in the runner (beyond status codes).

## 9. Deliverables map

| Requirement | Location |
|---|---|
| Dataset | `data/endpoints.json` (+ generator in `notebooks/`) |
| Code | `app/index.html`, `app/app.py`, `src/` |
| README | `README.md` |
| Report | `docs/project_report.md` (this file) |
| Presentation | `docs/presentation.pptx` / `.pdf` |
| Requirements | `requirements.txt` |
| Screenshots | `screenshots/` |
| Limitations & responsible use | §7 above + README §9–10 |
