# Project Status

## Source of truth

`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Current state

| Epic | Status | Notes |
|---|---|---|
| EPIC 00 — Project Foundation | Complete | Documentation/governance foundation is done. |
| EPIC 01 — Skeleton + Config + Healthcheck | Complete | Minimal FastAPI app, config layer, health route and health test exist. |
| EPIC 01.5 — Repo Alignment & Delivery Baseline | Current | Corrective alignment after audit. |
| EPIC 02 — Database + State Machine | Next | Must be implemented before intake/AI/routing/pipeline. |
| EPIC 03 — Intake API + Security + Idempotency | Not started | Depends on EPIC 02. |
| EPIC 04 — AI Classifier | Not started | Depends on EPIC 02/03. |
| EPIC 05 — Routing Engine | Not started | Depends on EPIC 04. |
| EPIC 06 — Bitrix24 Adapter Integration Pass | Partial early implementation | Existing adapter boundary must be audited and integrated after EPIC 02–05. Do not recreate from scratch. |
| EPIC 07 — Worker Pipeline | Not started | Depends on EPIC 02–06. |
| EPIC 08 — Admin Dashboard | Not started | Depends on pipeline and core statuses. |
| EPIC 09 — Tests + Security | Not started | Final hardening and full test matrix. |
| EPIC 10 — Portfolio Packaging | Not started | GitHub/Notion/HH packaging. |

Status in this file is the approved delivery baseline for future epic work.
The repository currently contains exploratory or early implementation files beyond that baseline; their presence does not mean those epics are accepted as complete.

## Current priority

Finish EPIC 01.5, then start EPIC 02.

## Important instruction for future agents

Do not continue Bitrix24 adapter work until Database, Intake API, AI Classifier, and Routing Engine are implemented.

Do not recreate the existing Bitrix24 adapter from scratch. During EPIC 06, audit and integrate existing code.

## Next functional epic

EPIC 02 — Database + State Machine.

Prompt:

`docs/prompts/02_database_cursor_prompt.md`
