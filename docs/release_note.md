# Release Note

Source of truth: `docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Title
AI Lead Intake for Bitrix24 - portfolio packaging release

## Summary
This release finalizes the public-facing packaging for the project. The repository is now presented as a demo/product prototype with a production-capable architecture and clear public-safe boundaries.

## Highlights
- Updated the README so the public-facing description matches the implemented baseline.
- Added public-safe Notion case structure and screenshot plan.
- Added synthetic demo requests and a local seed script for repeatable demos.
- Added a repeatable demo walkthrough, live demo script, and screenshot capture checklist.
- Tightened release and publication checklists.
- Kept the scope aligned with the staged epic plan and the source of truth.
- Confirmed the real Bitrix24 trial validation baseline in `legacy` CRM mode.
- Confirmed `review_needed` and admin manual action paths in the running app.

## Public-safe positioning
- Synthetic data only.
- No secrets or real PII in the repository.
- Demo-first delivery, not a commercial deployment.
- Production-capable architecture with room for future hardening.
- Demo data and seed flow are safe to share publicly.

## Use this text for GitHub
AI Lead Intake for Bitrix24 now has a finalized public-facing package for GitHub. The repository is positioned as a demo/product prototype with production-capable architecture, synthetic data only, and no secrets or real PII. The README, sample demo data, seed script, validation runbook, and portfolio assets now reflect the publication-ready and runtime-validated state.

## Use this text for Notion
AI Lead Intake for Bitrix24 is a production-capable demo/product prototype for CRM intake automation. It accepts incoming requests, classifies them with AI, routes them deterministically, syncs into Bitrix24, and sends uncertain cases to human review. The repository is public-safe, uses synthetic data, and now includes a confirmed local runtime baseline with a real Bitrix24 trial portal in `legacy` mode.

## Links
- README: `README.md`
- Notion case structure: `docs/notion_case.md`
- Screenshot plan: `docs/screenshots_plan.md`
- Demo walkthrough: `docs/demo_walkthrough.md`
- Demo script: `docs/demo_script.md`
- Screenshot capture checklist: `docs/screenshots_capture_checklist.md`
- Portfolio publication checklist: `docs/checklists/portfolio_publication_checklist.md`
- Real Bitrix24 validation runbook: `docs/bitrix24_trial_runbook.md`
- Demo requests: `demo_data/sample_requests.json`
- Seed helper: `scripts/seed_demo_data.py`
