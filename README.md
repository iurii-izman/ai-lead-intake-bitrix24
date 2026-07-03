# AI Lead Intake для Битрикс24

> Demo case / product prototype. This is not a commercial deployment.
> The architecture is production-capable; the first delivery is a portfolio/demo MVP.

Source of truth: `docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Status

Current repository baseline:
- EPIC 00 — complete
- EPIC 01 — complete
- EPIC 01.5 — complete
- EPIC 02–09 — implemented and passing current local checks
- EPIC 10 — complete

Validated local baseline:
- `pytest -q`
- `ruff check .`

Approved repository state is tracked in `docs/project_status.md`.

## What it is

AI Lead Intake for Bitrix24 is a production-capable demo-first backend prototype for:
- protected intake API;
- AI-based lead classification;
- deterministic routing;
- Bitrix24 CRM and task synchronization;
- human review for uncertain cases;
- masked operational admin visibility.

The system accepts an incoming request, stores it idempotently, classifies it through an AI boundary, applies routing rules, creates Bitrix24 entities, and keeps a processing timeline for review and debugging.

## What it demonstrates

- FastAPI application structure with explicit boundaries
- SQLite-backed MVP queue with portable domain model
- Pydantic validation and structured outputs
- Mock and real integration seams for AI and Bitrix24
- State machine, retry semantics, and idempotency
- Public-safe masking for logs, UI, and docs
- Basic Auth admin UI for operational review
- Testable worker orchestration and deterministic routing

## Architecture

High-level flow:

```text
Request -> Intake API -> DB queue -> Worker -> AI -> Routing -> Bitrix24 -> Task -> Review/Logs
```

Detailed architecture and data flow:
- [Architecture doc](./docs/architecture.md)
- [Implementation plan](./docs/implementation_plan.md)
- [Project status](./docs/project_status.md)

## Quick Start

### 1. Create environment file

```bash
copy .env.example .env
```

Or on Unix-like shells:

```bash
cp .env.example .env
```

The Docker Compose setup reads `.env`, not `.env.example`, so this copy step is required for the containerized demo path.

### 2. Start locally

```bash
docker compose up --build
```

Or run without Docker:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -e .[dev]
uvicorn app.main:app --reload
```

### 3. Open key endpoints

- Health: `/health`
- API docs: `/docs`
- Admin UI: `/`

## Demo Mode

Recommended demo-safe configuration:
- `AI_PROVIDER=mock`
- `BITRIX_MODE=mock`
- synthetic payloads only

This allows the full pipeline to run without OpenAI or Bitrix24 credentials.

Sample demo requests live in:
- [demo_data/sample_requests.json](./demo_data/sample_requests.json)

To seed demo requests into a local SQLite DB:

```bash
python scripts/seed_demo_data.py --database-url sqlite+pysqlite:///./demo.sqlite3
```

## Real Mode Boundaries

The repository also contains isolated seams for real integrations:
- `AI_PROVIDER=openai`
- `BITRIX_MODE=real`
- `BITRIX_CRM_MODE=universal|legacy`

These modes are present for architecture completeness, but the repository is still positioned as a demo/product prototype rather than a live production deployment.

## API

Primary public endpoint:

- `POST /api/v1/intake`
- `GET /api/v1/intake/{request_id}`

Current behavior:
- validates payload shape;
- requires `X-Webhook-Secret`;
- enforces idempotency by `idempotency_key`;
- rate-limits repeated submissions;
- stores masked request data and processing log;
- returns quickly without waiting for downstream processing;
- allows a protected lookup of the stored intake record by `request_id`.

Example request:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/intake ^
  -H "Content-Type: application/json" ^
  -H "X-Webhook-Secret: dev-webhook-secret" ^
  -d "{\"idempotency_key\":\"site-form-demo-0001\",\"source\":\"web_form\",\"message\":\"Need Bitrix24 CRM implementation support\"}"
```

## Admin UI

The admin surface is server-rendered and protected with Basic Auth.

It includes:
- dashboard queue view;
- request list and detail view;
- review queue;
- approve/retry/drop/reprocess actions;
- masked settings snapshot.

## Security

Public-safe rules for this repository:
- no secrets in git;
- no real PII;
- synthetic demo data only;
- masking in UI and logs;
- admin Basic Auth;
- intake webhook secret validation;
- release hygiene before publication.

Relevant docs:
- [Security checklist](./docs/checklists/security_checklist.md)
- [Portfolio publication checklist](./docs/checklists/portfolio_publication_checklist.md)

## Tests

Run:

```bash
pytest -q
ruff check .
```

Tests do not rely on real external network calls and use mock boundaries for AI and Bitrix24 behavior.

## Portfolio Assets

Public-safe packaging artifacts:
- [Notion case structure](./docs/notion_case.md)
- [Screenshot plan](./docs/screenshots_plan.md)
- [Release note](./docs/release_note.md)
- [Portfolio publication checklist](./docs/checklists/portfolio_publication_checklist.md)

## Documentation

- [Technical specification](./docs/ai_lead_intake_bitrix24_tz_v1_0.md)
- [Project brief](./docs/project_brief.md)
- [Architecture](./docs/architecture.md)
- [Implementation plan](./docs/implementation_plan.md)
- [Project status](./docs/project_status.md)
- [Epics](./docs/epics/)
- [Prompts](./docs/prompts/)

## Production Upgrade Path

The current codebase is intentionally demo-first. A stronger internal-production variant would typically add:
- PostgreSQL instead of SQLite;
- migrations;
- external queue or worker infrastructure;
- stronger auth and audit controls;
- deployment/monitoring profile;
- stricter operational guardrails.

The goal is to evolve the same boundaries, not to replace the whole system.

## Roadmap

- Finish packaging and public-safe presentation polish
- Expand publication assets and walkthrough materials
- Strengthen deployment and operations profile for internal-production evolution

## Next Epic

Recommended next post-MVP epic:
- [EPIC 11 — Demo Walkthrough & Visual Presentation](./docs/epics/EPIC_11_demo_walkthrough.md)
- [Prompt](./docs/prompts/11_demo_walkthrough_cursor_prompt.md)

## Disclaimer

This is a demo/product prototype. It is not a commercial deployment.
Architecture is production-capable; first delivery is portfolio/demo MVP.
