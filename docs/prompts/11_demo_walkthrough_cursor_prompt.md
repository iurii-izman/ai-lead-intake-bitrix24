# Cursor Prompt — EPIC 11 Demo Walkthrough & Visual Presentation

## Context
You are working in `C:\dev_bitrix24\ai_lead_intake_bitrix24`.

The repository baseline through EPIC 10 is already implemented and verified.
This epic is a post-MVP presentation and demo-enablement pass.

## Source of truth
`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Task
Prepare a polished, repeatable walkthrough layer for live demos and portfolio presentation.

You should:
- audit the current public docs and demo flow;
- produce a deterministic local walkthrough in mock mode;
- document what to show in the app, in which order, and why;
- add a screenshot capture checklist tied to the actual UI and masking rules;
- improve any public-facing packaging doc that is required to support the walkthrough.

## Files to create/change
- `docs/demo_walkthrough.md`
- `docs/demo_script.md`
- `docs/screenshots_capture_checklist.md`
- `README.md` if needed
- existing packaging docs if needed

## Implementation constraints
- Do not introduce new product scope unless a concrete demo blocker is found.
- Do not use real PII, real secrets, or real customer data.
- Keep the walkthrough aligned with mock-mode local execution.
- Keep the explanation tight, recruiter-friendly, and reproducible by another engineer.

## Non-goals
- No new platform features.
- No architectural rewrites.
- No frontend redesign.
- No commercial-claim positioning.

## Acceptance criteria
- A new reviewer can follow the local demo with minimal setup ambiguity.
- The walkthrough covers:
  - intake submission;
  - stored request retrieval;
  - worker/pipeline effect;
  - admin review path;
  - completed Bitrix result path;
  - masking/public-safety checks.
- Screenshot guidance is explicit and consistent with the current UI.
- Public docs remain accurate and public-safe.

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
- Presentation polish, CI/deployment hardening, or targeted post-MVP maintenance
