# Project Status

## Source of truth

`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Current state

| Epic | Repository state | Notes |
|---|---|---|
| EPIC 00 — Project Foundation | Complete | Foundation docs, ADRs, prompts, checklists, README draft, and repo rules exist. |
| EPIC 01 — Skeleton + Config + Healthcheck | Complete | FastAPI app factory, settings, health route, Docker artifacts, and config tests exist. |
| EPIC 01.5 — Repo Alignment & Delivery Baseline | Complete | Alignment pass was done, but this file and several prompts drifted behind the code and are now resynchronized. |
| EPIC 02 — Database + State Machine | Complete | SQLAlchemy models, enums, state machine, DB init path, and model/state tests exist. |
| EPIC 03 — Intake API + Security + Idempotency | Complete | Protected intake endpoint, idempotency, intake logging, and rate limiting exist and are tested. |
| EPIC 04 — AI Classifier | Complete | Mock/OpenAI provider boundary, schema validation, fallback behavior, and tests exist. |
| EPIC 05 — Routing Engine | Complete | YAML routing rules, deterministic decisions, fallback/review/drop paths, and tests exist. |
| EPIC 06 — Bitrix24 Adapter Integration Pass | Complete | Existing adapter boundary is integrated with field mapping, mock/real modes, CRM modes, retry semantics, persistence, and tests. |
| EPIC 07 — Worker Pipeline | Complete | In-process worker orchestrates intake → AI → routing → Bitrix → final states and is covered by pipeline tests. |
| EPIC 08 — Admin Dashboard | Complete | Basic Auth admin UI, request detail, review actions, settings snapshot, and masking are implemented and tested. |
| EPIC 09 — Tests + Security | Complete | Test suite and security hygiene checks are present; current local baseline is green under `pytest` and `ruff`. |
| EPIC 10 — Portfolio Packaging | Partial | Public-facing docs exist, but packaging is the main remaining hardening area. |

## Verified baseline

As of July 3, 2026:

- `pytest -q` passes.
- `ruff check .` passes.
- The repository contains a runnable demo-first implementation, not just exploratory scaffolding.

This file now tracks the actual repository baseline rather than the earlier staged plan snapshot.

## Current priority

Finish EPIC 10 — Portfolio Packaging and publication hygiene, then use the prompts in audit-and-gap-closure mode instead of recreate-from-scratch mode.

## Important instruction for future agents

Do not recreate already implemented layers from scratch.

For EPIC 02–09, treat the existing code as the baseline and work in this order:

1. audit the current implementation against the TЗ and acceptance criteria;
2. identify concrete gaps, regressions, or missing docs/tests;
3. close only those gaps;
4. update docs/prompts/status to reflect the real state.

The Bitrix24 adapter boundary already exists and must only be refined or extended through the existing service and client seams.

## Next recommended epic

EPIC 10 — Portfolio Packaging.

Prompt:

`docs/prompts/10_portfolio_packaging_cursor_prompt.md`
