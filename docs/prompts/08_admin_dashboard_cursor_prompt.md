# Cursor Prompt — EPIC 08 Admin Dashboard

## Context
Create the operational admin interface for review and visibility.
Inspect the current repository state before editing.
This epic is already implemented in the repository baseline.

## Source of truth
`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Task
Audit and refine the masked admin dashboard with Basic Auth protection.
Only fill verified gaps in UI behavior, masking, review actions, or admin tests/docs.

## Files to create/change
- `app/templates/*` or equivalent Jinja2 templates
- Admin route modules
- Basic Auth helpers
- Tests for auth and masking behavior

## Implementation constraints
- Keep the UI server-rendered and simple.
- Mask email, phone, and secrets in all visible views.
- Keep review actions small and explicit.
- Do not add a separate frontend framework.

## Non-goals
- No public frontend app.

## Acceptance criteria
- Admin pages are protected.
- PII is masked in the UI.
- Review actions are available.
- The UI stays aligned with the demo-first scope.
- Existing admin behavior is not rewritten without a concrete bug or acceptance gap.

## Final report format
## Done
- ...

## Files changed
- ...

## Branch / commit / PR
- Branch:
- Commit:
- Push:
- PR:

## How to verify
- ...

## Notes / assumptions
- ...

## Tree state
- Working tree is clean at the end of the epic.

## Next step
- EPIC 10 — Portfolio Packaging, unless a verified admin gap remains
