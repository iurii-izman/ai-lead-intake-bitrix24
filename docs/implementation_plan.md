# Implementation Plan

Current repository state: the codebase now contains an implemented baseline through EPIC 10. This plan remains the staged roadmap, but future work should use it in audit-and-gap-closure mode rather than assuming each epic still needs greenfield implementation.

## EPIC 00 — Project Foundation
- Goal: establish the documentation, governance, and delivery structure.
- Expected output: docs tree, ADRs, prompts, rules, checklists, README draft, `.gitignore`.
- Key files: `docs/project_brief.md`, `docs/architecture.md`, `docs/implementation_plan.md`, `AGENTS.md`, `.cursor/rules/*`.
- Acceptance criteria: no runtime code; all documents point at the v1.0 TЗ.
- Non-goals: any FastAPI, DB, AI, or Bitrix implementation.

## EPIC 01 — Skeleton + Config + Healthcheck
- Goal: create the minimal runnable application skeleton and health endpoint.
- Expected output: app entrypoint, settings, basic config, healthcheck, local run path.
- Key files: `app/main.py`, `app/config.py`, `app/api/health.py`.
- Acceptance criteria: app starts and returns a healthy status.
- Non-goals: intake logic, AI, routing, Bitrix sync.

## EPIC 01.5 — Repo Alignment & Delivery Baseline
- Goal: correct repository status after EPIC 00/01 and early Bitrix24 work.
- Expected output: updated README, project status, corrected prompts, delivery baseline files.
- Key files: `README.md`, `docs/project_status.md`, `docs/epics/EPIC_01_5_repo_alignment.md`, `docs/prompts/*`.
- Acceptance criteria: future work starts from EPIC 02 without ambiguity.
- Non-goals: functional runtime implementation.

## EPIC 02 — Database + State Machine
- Goal: define persistence and the request state machine.
- Expected output: schema, enums, migrations or MVP table creation strategy.
- Key files: database models, repositories, schema docs.
- Acceptance criteria: state transitions are explicit and testable.
- Non-goals: external integrations.

## EPIC 03 — Intake API + Security + Idempotency
- Goal: accept incoming requests safely and idempotently.
- Expected output: protected intake endpoint, duplicate detection, queue write.
- Key files: intake routes, request schemas, security helpers.
- Acceptance criteria: valid requests are accepted and duplicates are recognized.
- Non-goals: classification or CRM sync.

## EPIC 04 — AI Classifier
- Goal: classify requests and extract structured fields.
- Expected output: provider abstraction, mock mode, validated structured output.
- Key files: classifier service, provider client, schemas.
- Acceptance criteria: invalid or low-confidence output routes to review.
- Non-goals: routing or Bitrix writes.

## EPIC 05 — Routing Engine
- Goal: convert classifier output into a deterministic action plan.
- Expected output: rule evaluation and routing decisions.
- Key files: routing service, routing config.
- Acceptance criteria: repeated inputs produce stable decisions.
- Non-goals: CRM API logic.

## EPIC 06 — Bitrix24 Adapter Integration Pass
- Goal: audit and integrate the existing Bitrix24 adapter boundary instead of recreating it.
- Expected output: mock/real adapter, CRM mode selection, task creation.
- Key files: adapter client, mapping config, sync service.
- Acceptance criteria: adapter isolates API differences and handles errors predictably.
- Non-goals: UI or intake mechanics.

## EPIC 07 — Worker Pipeline
- Goal: orchestrate the end-to-end queue processing flow.
- Expected output: in-process worker, retries, transitions, timeline events.
- Key files: worker, processing orchestration, retry logic.
- Acceptance criteria: queue items move through the pipeline correctly.
- Non-goals: dashboard polish.

## EPIC 08 — Admin Dashboard
- Goal: provide operational visibility and manual control.
- Expected output: request list, detail view, review queue, actions.
- Key files: templates, admin routes, auth layer.
- Acceptance criteria: masked data and clear state visibility.
- Non-goals: public-facing UI features.

## EPIC 09 — Tests + Security
- Goal: validate the implementation and harden security behavior.
- Expected output: coverage for core flows, auth, masking, and failure cases.
- Key files: unit tests, integration tests, security tests.
- Acceptance criteria: tests pass without external network access.
- Non-goals: new features.

## EPIC 10 — Portfolio Packaging
- Goal: make the project presentable for GitHub, Notion, and hiring review.
- Expected output: polished README, screenshots plan, demo data plan, release notes.
- Key files: README, packaging docs, public-safe demo assets.
- Acceptance criteria: the repo can be reviewed safely without secrets or PII.
- Non-goals: production rollout tasks.

## EPIC 11 — Demo Walkthrough & Visual Presentation
- Goal: make the implemented baseline easier to present live and asynchronously.
- Expected output: repeatable demo walkthrough, presentation script, screenshot capture checklist.
- Key files: `docs/demo_walkthrough.md`, `docs/demo_script.md`, `docs/screenshots_capture_checklist.md`.
- Acceptance criteria: another reviewer can run and present the demo without hidden steps.
- Non-goals: new runtime features or architectural expansion.
