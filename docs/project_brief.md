# AI Lead Intake для Битрикс24

## Project overview
AI Lead Intake для Битрикс24 is a production-capable core for intake, AI classification, smart routing, and CRM synchronization for incoming leads and requests.

## Target role
Built for a specialist in AI automation for CRM and business processes, with an emphasis on portfolio-grade engineering discipline.

## Problem
Incoming requests are often processed manually, routed inconsistently, and lost across handoffs, which reduces response quality and CRM hygiene.

## Solution
The project sits between the incoming request source and Bitrix24, classifies the request with AI, selects a routing decision, creates CRM records and tasks, and sends uncertain cases to human review.

## Key data flow
`Request source -> intake API -> DB queue -> AI classifier -> routing engine -> Bitrix24 adapter -> task creation -> logs and admin review`

## MVP scope
- Intake endpoint with idempotency and webhook secret protection.
- SQLite-backed queue for the demo MVP.
- AI classification with mock and real provider modes.
- Routing by rules and confidence threshold.
- Bitrix24 sync in mock and real modes.
- Human review path for ambiguous cases.
- Admin UI for visibility and manual actions.

## Out of scope
- Multi-tenant SaaS.
- OAuth app for Bitrix24 marketplace.
- Celery/Redis queue in the MVP.
- React/Vue frontend.
- Enterprise-scale observability stack.
- Real customer data in the public repo.

## Delivery approach
Demo-first delivery with production-capable seams. The first release is a portfolio/demo MVP, but the architecture keeps clear seams for later production hardening.

## Stack
- Python 3.12
- FastAPI
- SQLite for demo MVP
- SQLAlchemy 2
- Pydantic
- Jinja2 + HTMX + Tailwind CDN
- pytest
- ruff

## References
- [Technical specification](./ai_lead_intake_bitrix24_tz_v1_0.md)
- [Architecture](./architecture.md)
- [Implementation plan](./implementation_plan.md)
- [Epics](./epics/)
- [ADRs](./adr/)
