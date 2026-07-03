# EPIC 11 — Demo Walkthrough & Visual Presentation

## Goal
Prepare a polished, repeatable demo and presentation layer for GitHub, Notion, HH, and live walkthrough use.

## Source of truth
`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Scope
- Demo runbook for local walkthrough.
- Scripted flow for intake → worker → admin review → completion.
- Public-safe screenshot capture guidance.
- Presentation-oriented artifacts that explain what to click, what to show, and what to avoid.
- Final reconciliation between repo messaging and actual demo steps.

## Out of scope
- No new product features.
- No architectural rewrites.
- No new external integrations.
- No real customer data or secrets.

## Expected files
- `docs/demo_walkthrough.md`
- `docs/demo_script.md`
- `docs/screenshots_capture_checklist.md`
- updates to `README.md` or public packaging docs if required

## Implementation notes
- Use only synthetic data and masked UI states.
- Prefer deterministic local steps that work in mock mode.
- Keep the demo path short enough for a recruiter or interviewer to follow in 5-10 minutes.
- If a missing runtime behavior blocks the walkthrough, fix only the concrete blocker and keep the change minimal.

## Acceptance criteria
- A new agent can run the local demo without guessing the sequence.
- The walkthrough covers intake, AI/routing outcome, review path, and Bitrix result paths at least at the UI/data level.
- Public-safe screenshot guidance is explicit and consistent with the current UI.
- The demo script does not depend on hidden tribal knowledge.

## Definition of Done
- Demo instructions are concrete, ordered, and executable.
- Visual presentation guidance is public-safe.
- The repo is easier to present live and asynchronously.
- Changes are committed, pushed, and handed off via a draft PR unless the user explicitly requests a direct main push.
- Working tree is clean at handoff.

## Status
Complete.

## Cursor prompt location
`docs/prompts/11_demo_walkthrough_cursor_prompt.md`
