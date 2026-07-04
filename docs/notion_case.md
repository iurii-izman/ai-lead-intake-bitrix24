# AI Lead Intake for Bitrix24

Source of truth: `docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Public-safe disclaimer

Demo case / product prototype. This is not a commercial deployment.
The architecture is production-capable; the first delivery is a portfolio/demo MVP.

## One-line summary

AI Lead Intake for Bitrix24 is a backend automation prototype that accepts incoming requests, classifies them through an AI boundary, routes them deterministically, creates CRM records and tasks in Bitrix24, and sends uncertain cases to human review.

## Problem

Incoming requests are often handled manually, routed inconsistently, and partially lost between first contact, CRM entry, and follow-up execution. That creates delays, weak CRM hygiene, and poor visibility into why a request was routed or dropped.

## Solution

This project inserts a controlled backend layer between the intake source and Bitrix24:

- a protected intake API accepts and stores requests quickly;
- a DB-backed queue and in-process worker process them asynchronously;
- an AI classification boundary extracts category, priority, intent, and a draft reply;
- a deterministic routing engine decides whether to route, review, or drop;
- a Bitrix24 adapter creates CRM and task entities through mock or real seams;
- an admin dashboard exposes masked request data, timeline logs, and manual actions.

## What was built

- FastAPI app with app factory, config layer, and Docker path
- SQLite-backed MVP queue with explicit request lifecycle
- protected `POST /api/v1/intake` and `GET /api/v1/intake/{request_id}`
- mock and real AI provider seams
- mock and real Bitrix24 seams
- universal and legacy Bitrix CRM modes
- server-rendered admin UI with Basic Auth
- manual actions for `approve`, `retry`, `drop`, and `reprocess-ai`
- pytest and ruff validation baseline

## Architecture

High-level flow:

```text
Request -> Intake API -> DB queue -> Worker -> AI -> Routing -> Bitrix24 -> Task -> Review/Logs
```

Design priorities:
- explicit service boundaries;
- idempotent intake behavior;
- observable state transitions;
- public-safe masking;
- no hard dependency on real provider calls for tests and demos.

## Confirmed runtime baseline

The repository is not only test-green; it was also exercised in a running local environment.

Confirmed as of July 4, 2026:

- `pytest -q` passes
- `ruff check .` passes
- the app runs locally through Docker Compose
- the real Bitrix24 portal path was validated with:
  - `AI_PROVIDER=mock`
  - `BITRIX_MODE=real`
  - `BITRIX_CRM_MODE=legacy`
- the happy path completed with created `crm.lead` and `task` records
- `review_needed` behavior was reproduced in the running app
- admin actions were exercised against runtime records:
  - `Approve`
  - `Reprocess AI`
  - `Retry Bitrix`
  - `Drop`

Important nuance:
- `universal` mode failed against the tested trial portal for `crm.item.add`
- `legacy` mode is the confirmed working mode for that portal baseline

## Why this is a strong portfolio case

- It is not just CRUD or scaffolding; it models a real intake-to-CRM workflow.
- It includes AI integration boundaries without coupling the core to one provider.
- It includes deterministic routing and human-in-the-loop behavior.
- It includes retry semantics, admin controls, and runtime observability.
- It was validated both by tests and by a real Bitrix24 trial integration pass.

## Public-safe constraints

- synthetic data only
- no committed secrets
- masking in logs and UI
- no claims of commercial production rollout
- no real customer PII in repository artifacts

## Trade-offs

This is intentionally a demo-first MVP, so several choices are deliberately lightweight:

- SQLite instead of PostgreSQL
- in-process worker instead of external queue infrastructure
- Basic Auth admin instead of richer RBAC
- Jinja2 server-rendered admin UI instead of SPA frontend
- trial-portal validation instead of hardened production deployment

Those trade-offs preserve a production-capable structure while keeping the demo path realistic and reviewable.

## Current known boundary

The remaining unvalidated major path is:
- `AI_PROVIDER=openai` against the real Bitrix24 path

That path is implementation-ready, but was intentionally paused because OpenAI credits were unavailable during the validation pass.

## Suggested visuals

Use these visuals in Notion, HH, or a portfolio PDF:

- architecture diagram
- dashboard queue view
- request detail page
- `review_needed` case
- completed Bitrix result
- Bitrix24 task / lead confirmation

## Links

- [README](./../README.md)
- [Architecture](./architecture.md)
- [Project status](./project_status.md)
- [Bitrix24 trial validation runbook](./bitrix24_trial_runbook.md)
- [Demo walkthrough](./demo_walkthrough.md)
