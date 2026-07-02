# AI Lead Intake для Битрикс24

Source of truth: `docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Status
Project foundation is complete. Implementation will proceed by epics.

## What it is
A production-capable core for intake, AI classification, smart routing, and Bitrix24 synchronization for incoming leads and requests.

## What it demonstrates
- FastAPI-style backend structure
- AI structured outputs
- Bitrix24 integration boundary
- Human-in-the-loop review
- Idempotency and retry thinking
- PII masking and operational hygiene

## Architecture
See [docs/architecture.md](./docs/architecture.md).

## Development approach
Production-capable architecture with demo-first delivery. The first working release is a portfolio/demo MVP, not a commercial deployment.

## Demo vs Production
This is a demo/product prototype. It is not a commercial deployment.
Architecture is production-capable; first delivery is portfolio/demo MVP.

## Repository
- GitHub: https://github.com/iurii-izman/ai-lead-intake-bitrix24
- Default branch: `main`
- Current stage: EPIC 00 complete, EPIC 01 next

## Documentation
- [Technical specification](./docs/ai_lead_intake_bitrix24_tz_v1_0.md)
- [Project brief](./docs/project_brief.md)
- [Architecture](./docs/architecture.md)
- [Implementation plan](./docs/implementation_plan.md)
- [Epics](./docs/epics/)
- [ADRs](./docs/adr/)
- [Prompts](./docs/prompts/)
- [Checklists](./docs/checklists/)

## Roadmap
See [docs/implementation_plan.md](./docs/implementation_plan.md).

## Next step
Start EPIC 01 using [docs/prompts/01_skeleton_cursor_prompt.md](./docs/prompts/01_skeleton_cursor_prompt.md).

## Disclaimer
This is a demo/product prototype. It is not a commercial deployment.
Architecture is production-capable; first delivery is portfolio/demo MVP.
