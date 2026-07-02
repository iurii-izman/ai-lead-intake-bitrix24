# Cursor Prompt — EPIC 08 Admin Dashboard

## Context
Create the operational admin interface for review and visibility.
Inspect the current repository state before editing and keep the UI scope narrow.

## Source of truth
`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Task
Build the masked admin dashboard with Basic Auth protection.

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
- EPIC 09 — Tests + Security
