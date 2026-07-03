# EPIC 01.5 — Repo Alignment & Delivery Baseline

## Goal

Align the repository after the initial foundation and skeleton work, correct project status, update prompts, and prepare the project for EPIC 02.

## Why this epic exists

EPIC 00 and EPIC 01 are effectively complete, but the repository status and prompts need correction.

Also, Bitrix24 adapter work was partially implemented early. This must be recorded so future work integrates it instead of rewriting it.

## Source of truth

`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Scope

- Update README project status.
- Create/update `docs/project_status.md`.
- Update EPIC 01 actual completion status.
- Update EPIC 06 actual completion status.
- Update prompts EPIC 02–07 with correct constraints.
- Add GitHub issues planning document.
- Add delivery baseline files if still missing:
  - `.env.example`
  - `Dockerfile`
  - `docker-compose.yml`
- Add a minimal config test if appropriate:
  - `tests/test_config.py`

## Out of scope

- No database models.
- No intake API.
- No AI classifier.
- No routing engine.
- No worker pipeline.
- No dashboard.
- No new Bitrix24 adapter work.
- No new TЗ version.

## Acceptance criteria

- README reflects the correct current stage.
- `docs/project_status.md` exists and is accurate.
- EPIC 01 is marked complete.
- EPIC 06 is marked partial early implementation / integration pending.
- Prompts EPIC 02–07 prevent accidental rework and scope creep.
- Missing delivery baseline files are added if absent.
- No secrets or real PII are added.
- No functional application features are introduced.
- Repository is ready for EPIC 02.

## Definition of Done

- All alignment documents are updated.
- Future Cursor agents can clearly see the current state.
- EPIC 02 can be started without ambiguity.
- Existing Bitrix24 adapter is protected from accidental rewrite.
