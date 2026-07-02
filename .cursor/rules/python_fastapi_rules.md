# Python / FastAPI Rules

Source of truth: `docs/ai_lead_intake_bitrix24_tz_v1_0.md`

- Use Python 3.12.
- Use FastAPI for the web layer.
- Use Pydantic for request and response validation.
- Use SQLAlchemy 2 for persistence.
- Use `pydantic-settings` for configuration.
- Keep API, services, integrations, models, and utils separated.
- Do not place heavy business logic in route handlers.
- Do not hardcode secrets.
