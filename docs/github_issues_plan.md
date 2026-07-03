# GitHub Issues Plan

## [EPIC 01.5] Repo Alignment & Delivery Baseline

## Goal
Align the repository after audit, correct project status, update prompts, and add missing delivery baseline files.

## Source of truth
`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Scope
- Update README and project status.
- Add EPIC 01.5 epic doc.
- Update EPIC 01 and EPIC 06 status notes.
- Correct prompts for EPIC 02–07.
- Add `.env.example`, `Dockerfile`, and `docker-compose.yml` if missing.
- Add issue planning doc for later epics.

## Non-goals
- No functional runtime implementation.
- No DB, intake, AI, routing, worker, dashboard, or new Bitrix work.

## Acceptance criteria
- Repository status is explicit and future epic order is unambiguous.
- Existing Bitrix24 adapter work is protected from rewrite.
- Missing delivery baseline files exist.

## Cursor prompt
`docs/epics/EPIC_01_5_repo_alignment.md`

## Labels suggestion
`epic`, `docs`, `repo-alignment`, `governance`

---

## [EPIC 02] Database + State Machine

## Goal
Define persistence primitives and the explicit intake request lifecycle.

## Source of truth
`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Scope
- Database models.
- State enum and transition rules.
- Processing logs.
- Pydantic schemas for persistence-facing structures.
- Tests for models and transitions.

## Non-goals
- No intake API.
- No AI calls.
- No routing engine.
- No worker pipeline.
- No Bitrix24 adapter changes.

## Acceptance criteria
- Tables for `intake_requests`, `ai_classifications`, `routing_decisions`, `bitrix_entities`, and `processing_logs` can be created.
- State transitions are explicit and testable.
- No external network calls are made in tests.

## Cursor prompt
`docs/prompts/02_database_cursor_prompt.md`

## Labels suggestion
`epic`, `backend`, `database`, `state-machine`

---

## [EPIC 03] Intake API + Security + Idempotency

## Goal
Accept incoming requests safely, validate them, and store them idempotently.

## Source of truth
`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Scope
- Intake API endpoint.
- Secret validation.
- Idempotency key handling.
- Processing log creation for intake receipt.
- Tests for success and rejection paths.

## Non-goals
- No AI classification.
- No Bitrix24 calls.
- No routing logic.
- No worker pipeline.

## Acceptance criteria
- Valid request returns `202`.
- Duplicate idempotency key returns the existing request.
- Invalid secret returns `401`.
- Invalid payload returns `422`.

## Cursor prompt
`docs/prompts/03_intake_api_cursor_prompt.md`

## Labels suggestion
`epic`, `backend`, `api`, `security`

---

## [EPIC 04] AI Classifier

## Goal
Implement AI provider abstraction and classification persistence with safe fallback behavior.

## Source of truth
`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Scope
- Mock classifier path.
- OpenAI provider boundary.
- Structured output validation.
- Classification persistence.
- Tests for valid, invalid, and low-confidence outcomes.

## Non-goals
- No routing engine.
- No Bitrix24 calls.
- No worker orchestration.

## Acceptance criteria
- `AI_PROVIDER=mock` works without API keys.
- OpenAI boundary is isolated behind a provider/client seam.
- Invalid or low-confidence output routes to review semantics.
- Tests make no real network calls.

## Cursor prompt
`docs/prompts/04_ai_classifier_cursor_prompt.md`

## Labels suggestion
`epic`, `backend`, `ai`, `integration-boundary`

---

## [EPIC 05] Routing Engine

## Goal
Convert AI classification results into deterministic routing decisions.

## Source of truth
`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Scope
- Routing config file.
- Deterministic top-down rules.
- Fallback route behavior.
- Spam/drop handling.
- Tests for rule evaluation.

## Non-goals
- No Bitrix24 calls.
- No worker pipeline.
- No adapter rewrite.

## Acceptance criteria
- Reads `config/routing.yaml`.
- Applies top-down rules with explicit fallback.
- Uses safe template formatting and no `eval`.
- Tests cover main decision paths.

## Cursor prompt
`docs/prompts/05_routing_engine_cursor_prompt.md`

## Labels suggestion
`epic`, `backend`, `routing`, `rules-engine`

---

## [EPIC 06] Bitrix24 Adapter Integration Pass

## Goal
Audit and integrate the existing Bitrix24 adapter boundary instead of recreating it.

## Source of truth
`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Scope
- Audit existing adapter and tests.
- Confirm mock/real and universal/legacy support.
- Integrate with routing decisions, `bitrix_entities`, processing logs, and state machine.
- Add missing tests or docs only where required.

## Non-goals
- No adapter rewrite from scratch.
- No OAuth marketplace work.
- No unrelated business-logic changes.

## Acceptance criteria
- Existing adapter capabilities are audited and documented.
- Integration uses existing boundaries.
- Retry/backoff and failure semantics remain covered by tests.

## Cursor prompt
`docs/prompts/06_bitrix24_adapter_cursor_prompt.md`

## Labels suggestion
`epic`, `backend`, `bitrix24`, `integration`

---

## [EPIC 07] Worker Pipeline

## Goal
Orchestrate the existing services into a bounded in-process processing pipeline.

## Source of truth
`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Scope
- Worker loop for `received` and `failed_retryable`.
- Retry handling.
- Confidence gate and review handling.
- Bitrix sync orchestration.
- Step-by-step processing logs.

## Non-goals
- No rewrite of AI, routing, or Bitrix services.
- No external queue infrastructure.

## Acceptance criteria
- Processes `received` and retryable records.
- Low confidence goes to review.
- Spam/drop goes to dropped.
- Temporary Bitrix failures go to `failed_retryable` and then `failed` after retry exhaustion.

## Cursor prompt
`docs/prompts/07_worker_pipeline_cursor_prompt.md`

## Labels suggestion
`epic`, `backend`, `worker`, `orchestration`

---

## [EPIC 08] Admin Dashboard

## Goal
Provide operational visibility and manual control for masked demo/admin workflows.

## Source of truth
`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Scope
- Request list and detail views.
- Review actions.
- Basic Auth protection.
- Masked data presentation.

## Non-goals
- No public-facing UI.
- No new core pipeline behavior.

## Acceptance criteria
- Review queue is visible.
- Sensitive fields are masked.
- Manual actions operate on existing service boundaries.

## Cursor prompt
`docs/prompts/08_admin_dashboard_cursor_prompt.md`

## Labels suggestion
`epic`, `backend`, `admin`, `ui`

---

## [EPIC 09] Tests + Security

## Goal
Harden the implementation and validate the full demo-safe behavior.

## Source of truth
`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Scope
- Expanded automated test matrix.
- Security hygiene checks.
- Failure-case coverage.
- Mock-only integration tests.

## Non-goals
- No new product features.
- No real external network calls.

## Acceptance criteria
- Tests cover happy paths and edge cases.
- Security-sensitive behavior is explicitly verified.
- No real AI or Bitrix24 traffic is used in tests.

## Cursor prompt
`docs/prompts/09_tests_security_cursor_prompt.md`

## Labels suggestion
`epic`, `tests`, `security`, `hardening`

---

## [EPIC 10] Portfolio Packaging

## Goal
Prepare the repository for GitHub, Notion, and hiring/portfolio review.

## Source of truth
`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Scope
- Public-safe README and packaging docs.
- Screenshot/demo plan.
- Release note and publication checklist.

## Non-goals
- No runtime feature work.
- No production rollout tasks.

## Acceptance criteria
- Repo can be reviewed without secrets or PII.
- Documentation clearly frames the project as demo/product prototype.
- Portfolio materials are consistent with the source of truth.

## Cursor prompt
`docs/prompts/10_portfolio_packaging_cursor_prompt.md`

## Labels suggestion
`epic`, `docs`, `portfolio`, `packaging`
