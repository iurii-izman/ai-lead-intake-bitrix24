# EPIC 00 — Project Foundation

## Goal
Prepare the documentation, operating rules, and delivery structure for the project before any runtime code is written.

## Source of truth
`docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Scope
- Create the documentation backbone for the project.
- Define epics, ADRs, prompts, rules, checklists, and reporting conventions.
- Align the repo for staged Cursor-driven implementation.
- Establish branch, commit, review, and quality-gate expectations.

## Out of scope
- No FastAPI app.
- No database models or migrations.
- No AI classifier or Bitrix24 adapter.
- No Dockerfile, docker-compose, or pyproject.toml.
- No secrets, `.env`, logs, or real PII.
- No functional runtime code of the application.

## Expected files
- `docs/project_brief.md`
- `docs/architecture.md`
- `docs/implementation_plan.md`
- `docs/epics/EPIC_00_foundation.md` through `docs/epics/EPIC_10_portfolio_packaging.md`
- `docs/adr/ADR_001_stack.md` through `docs/adr/ADR_006_demo_vs_production.md`
- `docs/prompts/00_foundation_cursor_prompt.md` through `docs/prompts/10_portfolio_packaging_cursor_prompt.md`
- `docs/checklists/*.md`
- `.cursor/rules/*.md`
- `AGENTS.md`
- `README.md`
- `.gitignore`

## Implementation notes
- Keep the project anchored to the v1.0 TЗ only.
- If later work requires a new technology or architectural shift, record it in ADR first.
- Every future epic should be executable in isolation and should not require ad hoc re-planning.
- Repository guidance must stay practical: demo-first delivery, production-capable seams, no overengineering.
- `docs/github_workflow.md` is allowed as a supporting artifact if useful for workflow clarity.

## Acceptance criteria
- The repo contains the complete documentation skeleton.
- Every required doc references `docs/ai_lead_intake_bitrix24_tz_v1_0.md`.
- There is no application runtime code.
- There are no secrets, `.env` files, SQLite DB files, or logs.
- Foundation files describe the exact path for EPIC 01 and beyond.

## Definition of Done
- `docs/` structure created.
- Epics, ADRs, prompts, checklists, and rules created.
- `AGENTS.md`, `README.md`, and `.gitignore` created.
- Foundation docs are internally consistent.
- No scope creep into runtime implementation.

## Cursor prompt location
`docs/prompts/00_foundation_cursor_prompt.md`
