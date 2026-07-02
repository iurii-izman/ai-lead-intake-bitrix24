# Testing Rules

Source of truth: `docs/ai_lead_intake_bitrix24_tz_v1_0.md`

- No real external network calls in tests.
- Mock OpenAI.
- Mock Bitrix24.
- Add unit tests for services.
- Add integration tests for pipeline flows.
- Cover duplicates, low confidence, invalid AI output, spam, and retryable Bitrix errors.
