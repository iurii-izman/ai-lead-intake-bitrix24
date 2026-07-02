# Cursor Prompt — EPIC 07 Worker Pipeline

## Context
The queue, classifier, routing, and adapter are ready to be orchestrated together.
Inspect the current repository state first and avoid touching unrelated files.

## Source of truth
`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Task
Implement the in-process worker and full processing pipeline.

## Files to create/change
- `app/services/worker.py` or equivalent orchestrator
- Pipeline/service glue code
- Retry handling and status transition code
- Tests for happy path, review path, drop path, and retryable failure path

## Implementation constraints
- Process queue items in a clear, bounded loop.
- Keep the worker in-process for the MVP.
- Preserve traceable status transitions and timeline events.
- Do not add external queue infrastructure.

## Non-goals
- No external queue infrastructure.

## Acceptance criteria
- Items move through the pipeline correctly.
- Review, dropped, and failed paths are explicit.
- Retry behavior is bounded and testable.

## Final report format
## Done
- ...

## Files changed
- ...

## How to verify
- ...

## Notes / assumptions
- ...

## Next step
- EPIC 08 — Admin Dashboard
