# AI Lead Intake для Битрикс24

> Demo case / product prototype. This is not a commercial deployment.
> The architecture is production-capable; the first delivery is a portfolio/demo MVP.

Source of truth: `docs/ai_lead_intake_bitrix24_tz_v1_0.md`

## Status
All staged epics are complete for the current portfolio/demo scope. The repository is ready for publication and maintenance.

## What it is
A production-capable core for intake, AI classification, smart routing, and Bitrix24 synchronization for incoming leads and requests.

## What it demonstrates
- FastAPI-style backend structure
- AI structured outputs
- Bitrix24 integration boundary
- Human-in-the-loop review
- Idempotency and retry thinking
- PII masking and operational hygiene

## What is intentionally excluded from the public repo
- Real client PII
- Secrets and `.env` files
- Commercial claims about a live deployment
- SaaS, multitenancy, OAuth marketplace packaging
- React/Celery/Kafka/RabbitMQ in the MVP

## Architecture
See [docs/architecture.md](./docs/architecture.md).

## Public-safe packaging
- [Portfolio publication checklist](./docs/checklists/portfolio_publication_checklist.md)
- [Release checklist](./docs/checklists/release_checklist.md)
- [Release note](./docs/release_note.md)
- [Notion case structure](./docs/notion_case.md)
- [Screenshot plan](./docs/screenshots_plan.md)

## Development approach
Demo-first delivery with production-capable seams. The first working release is a portfolio/demo MVP, not a commercial deployment.

## Repository
- GitHub: https://github.com/iurii-izman/ai-lead-intake-bitrix24
- Default branch: `main`
- Current stage: EPIC 10 complete, portfolio packaging finalized

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
For future product hardening, start a new branch and document the scope separately.

## Delivery rule
Each epic should finish with a clean working tree, a committed feature branch, a pushed branch, and a draft PR unless a direct `main` push is explicitly requested.

## Disclaimer
This is a demo/product prototype. It is not a commercial deployment.
Architecture is production-capable; first delivery is portfolio/demo MVP.
