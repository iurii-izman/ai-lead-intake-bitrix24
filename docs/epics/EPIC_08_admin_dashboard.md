# EPIC 08 — Admin Dashboard

## Goal
Provide a safe, masked operational UI for review and monitoring.

## Source of truth
`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Scope
- Queue views.
- Request details.
- Review actions.
- Basic Auth protection.

## Out of scope
- Public customer-facing UI.
- Rich frontend framework work.

## Expected files
- Templates
- Admin routes
- Auth helpers

## Implementation notes
- Mask email, phone, and secrets in views.
- Keep the UI compact and readable.
- Any UI architecture change needs an ADR.
- Any new frontend paradigm outside this epic requires an ADR first.

## Acceptance criteria
- Admin users can review and act on requests safely.

## Definition of Done
- Dashboard is functional, masked, and authenticated.
- Review actions work without exposing sensitive data.
- Changes are committed, pushed, and handed off via a draft PR unless the user explicitly requests a direct main push.
- Working tree is clean at handoff.

## Cursor prompt location
`docs/prompts/08_admin_dashboard_cursor_prompt.md`
