# AI Lead Intake для Битрикс24

> Demo case / product prototype. This is not a commercial deployment.
> The architecture is production-capable; the first delivery is a portfolio/demo MVP.

Source of truth: `docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Status

Current stage:
- EPIC 00 — complete
- EPIC 01 — complete
- EPIC 01.5 — current: repository alignment and delivery baseline
- EPIC 02 — next functional epic: Database + State Machine
- EPIC 06 — Bitrix24 adapter boundary was partially implemented early and must be integrated after EPIC 02–05

Approved status is tracked in `docs/project_status.md`.
The repository contains exploratory code beyond the approved epic sequence; future work should follow the documented epic order instead of assuming every existing file is final.

## What it is

A production-capable demo-first backend prototype for intake, AI classification, routing, and Bitrix24 synchronization boundaries.

## Development approach

Demo-first delivery with production-capable seams. The first working release is a portfolio/demo MVP, not a commercial deployment.

## Repository

- GitHub: https://github.com/iurii-izman/ai-lead-intake-bitrix24
- Default branch: `main`

## Documentation

- [Technical specification](./docs/ai_lead_intake_bitrix24_tz_v1_0.md)
- [Project status](./docs/project_status.md)
- [Implementation plan](./docs/implementation_plan.md)
- [EPIC 02 prompt](./docs/prompts/02_database_cursor_prompt.md)
- [Epics](./docs/epics/)
- [Prompts](./docs/prompts/)

## Next step

Close EPIC 01.5, then start EPIC 02 — Database + State Machine.

## Delivery note

Production-capable architecture, demo-first delivery. Do not treat the repository as an end-to-end production-ready system yet.

## Disclaimer

This is a demo/product prototype. It is not a commercial deployment.
Architecture is production-capable; first delivery is portfolio/demo MVP.
