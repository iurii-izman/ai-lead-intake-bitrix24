# EPIC 07 — Worker Pipeline

## Goal
Orchestrate the end-to-end processing flow from queue to final state.

## Source of truth
`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Scope
- In-process worker.
- Retry handling.
- State transitions.

## Out of scope
- External queue infrastructure.
- Advanced observability stack.

## Expected files
- Worker orchestration
- Retry logic
- Pipeline tests

## Implementation notes
- Preserve traceability across steps.
- Keep retry semantics explicit.
- No scope extension without ADR updates.
- Any new orchestration primitive beyond this epic requires an ADR first.

## Acceptance criteria
- Queue items move through the full pipeline predictably.

## Definition of Done
- The MVP pipeline is observable and repeatable.
- Retry and terminal states are covered by tests.
- Changes are committed, pushed, and handed off via a draft PR unless the user explicitly requests a direct main push.
- Working tree is clean at handoff.

## Cursor prompt location
`docs/prompts/07_worker_pipeline_cursor_prompt.md`
