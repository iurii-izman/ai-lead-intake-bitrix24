# Cursor Prompt — EPIC 00 Project Foundation

Ты работаешь в локальном проекте:

```text
C:\dev_bitrix24\ai_lead_intake_bitrix24
```

Главный источник истины:

```text
docs/ai_lead_intake_bitrix24_tz_v1_0.md
```

Важно: это единственная финальная версия ТЗ. Не создавай новую версию ТЗ, не создавай `v2.0`, не переименовывай текущий файл. Если в старых материалах есть упоминания `v2.0`, считай это устаревшим названием. Вся разработка ведётся по `ai_lead_intake_bitrix24_tz_v1_0.md`.

---

## Роль

Ты senior AI coding agent, backend engineer, solution architect и technical writer.

Твоя задача — выполнить:

```text
EPIC 00 — Project Foundation
```

Это подготовительный этап. Не писать функциональный код приложения.

---

## Цель EPIC 00

Подготовить фундамент современной AI-разработки проекта:

- структуру документации;
- epics;
- ADR;
- Cursor prompts;
- AGENTS.md;
- `.cursor/rules`;
- checklists;
- README draft;
- `.gitignore`;
- Git/GitHub workflow;
- quality gates.

После этого проекта можно безопасно переходить к EPIC 01 — Skeleton + Config + Healthcheck.

---

## Критические ограничения

Запрещено:

- создавать FastAPI app;
- создавать `app/main.py`;
- создавать БД;
- создавать Dockerfile;
- создавать docker-compose;
- создавать pyproject.toml;
- создавать AI classifier;
- создавать Bitrix24 adapter;
- создавать dashboard;
- писать runtime-код приложения;
- добавлять реальные секреты;
- создавать `.env`;
- использовать реальные персональные данные;
- создавать SQLite DB;
- создавать logs;
- добавлять React/Vue/Celery/Redis/OAuth/SaaS/Kubernetes;
- менять или дублировать ТЗ.

На этом этапе создаются только foundation-документы, rules, prompts, README draft и `.gitignore`.

---

## Что нужно сделать

### 1. Проверь наличие ТЗ

Проверь, что существует файл:

```text
docs/ai_lead_intake_bitrix24_tz_v1_0.md
```

Если файл есть — используй его как source of truth.  
Если файла нет — остановись и сообщи, что отсутствует главный документ.

---

### 2. Создай структуру документации

Создай папки:

```text
docs/epics
docs/adr
docs/prompts
docs/checklists
.cursor/rules
```

---

### 3. Создай основные docs

Создай файлы:

```text
docs/project_brief.md
docs/architecture.md
docs/implementation_plan.md
```

#### `docs/project_brief.md`

Содержимое должно включать:

- название проекта;
- краткое описание;
- целевую роль;
- проблему;
- решение;
- ключевой data flow;
- MVP scope;
- out of scope;
- demo-first / production-capable подход;
- стек;
- ссылки на:
  - `docs/ai_lead_intake_bitrix24_tz_v1_0.md`;
  - `docs/architecture.md`;
  - `docs/implementation_plan.md`;
  - `docs/epics/`;
  - `docs/adr/`.

#### `docs/architecture.md`

Содержимое должно включать:

- архитектурный контекст;
- Mermaid-схему data flow;
- описание слоёв:
  - API Layer;
  - DB Queue;
  - In-process Worker;
  - AI Classifier;
  - Routing Engine;
  - Bitrix24 Adapter;
  - Admin Dashboard;
  - Processing Logs.
- state machine;
- mock/real AI mode;
- mock/real Bitrix24 mode;
- universal/legacy Bitrix CRM mode;
- demo vs production notes;
- production upgrade path.

#### `docs/implementation_plan.md`

Содержимое должно описывать этапы:

```text
EPIC 00 — Project Foundation
EPIC 01 — Skeleton + Config + Healthcheck
EPIC 02 — Database + State Machine
EPIC 03 — Intake API + Security + Idempotency
EPIC 04 — AI Classifier
EPIC 05 — Routing Engine
EPIC 06 — Bitrix24 Adapter
EPIC 07 — Worker Pipeline
EPIC 08 — Admin Dashboard
EPIC 09 — Tests + Security
EPIC 10 — Portfolio Packaging
```

Для каждого этапа добавить:

- цель;
- expected output;
- key files;
- acceptance criteria;
- non-goals.

---

### 4. Создай EPIC-файлы

Создай:

```text
docs/epics/EPIC_00_foundation.md
docs/epics/EPIC_01_skeleton.md
docs/epics/EPIC_02_database.md
docs/epics/EPIC_03_intake_api.md
docs/epics/EPIC_04_ai_classifier.md
docs/epics/EPIC_05_routing_engine.md
docs/epics/EPIC_06_bitrix24_adapter.md
docs/epics/EPIC_07_worker_pipeline.md
docs/epics/EPIC_08_admin_dashboard.md
docs/epics/EPIC_09_tests_security.md
docs/epics/EPIC_10_portfolio_packaging.md
```

Каждый EPIC должен иметь структуру:

```markdown
# EPIC XX — Title

## Goal

## Source of truth

## Scope

## Out of scope

## Expected files

## Implementation notes

## Acceptance criteria

## Definition of Done

## Cursor prompt location
```

Требования:

- EPIC 00 сделать максимально подробным.
- EPIC 01–10 сделать компактными, но полезными.
- В каждом EPIC указать source of truth:
  `docs/ai_lead_intake_bitrix24_tz_v1_0.md`.
- В каждом EPIC указать, что нельзя выходить за scope без обновления ADR.

---

### 5. Создай ADR

Создай:

```text
docs/adr/ADR_001_stack.md
docs/adr/ADR_002_bitrix24_integration_mode.md
docs/adr/ADR_003_worker_strategy.md
docs/adr/ADR_004_ai_structured_outputs.md
docs/adr/ADR_005_security_privacy.md
docs/adr/ADR_006_demo_vs_production.md
```

Каждый ADR должен иметь структуру:

```markdown
# ADR XXX — Title

## Status
Accepted

## Context

## Decision

## Consequences

## Alternatives considered
```

Содержание решений:

### ADR 001 — Stack

- Python 3.12;
- FastAPI;
- SQLite for Demo MVP;
- SQLAlchemy 2;
- Pydantic;
- Jinja2 + HTMX + Tailwind CDN;
- Docker Compose later;
- pytest;
- ruff.

### ADR 002 — Bitrix24 Integration Mode

- `BITRIX_MODE=mock|real`;
- `BITRIX_CRM_MODE=universal|legacy`;
- primary CRM mode: `crm.item.add`;
- legacy fallback: `crm.lead.add`;
- tasks: `tasks.task.add`;
- field mapping through `config/field_mapping.yaml`.

### ADR 003 — Worker Strategy

- DB queue + in-process worker for Demo MVP;
- no Celery/Redis in MVP;
- architecture must allow later replacement with external queue.

### ADR 004 — AI Structured Outputs

- `AI_PROVIDER=mock|openai`;
- provider abstraction;
- Structured Outputs / JSON Schema;
- Pydantic validation;
- invalid output / low confidence → `review_needed`.

### ADR 005 — Security & Privacy

- no secrets in repo;
- `.env` ignored;
- synthetic demo data only;
- PII masking in logs/UI/screenshots;
- Basic Auth for admin;
- `X-Webhook-Secret` for intake endpoint;
- no real PII in public repo.

### ADR 006 — Demo vs Production

- production-first design;
- demo-first delivery;
- no enterprise overengineering in MVP;
- roadmap to internal production app.

---

### 6. Создай prompts

Создай:

```text
docs/prompts/00_foundation_cursor_prompt.md
docs/prompts/01_skeleton_cursor_prompt.md
docs/prompts/02_database_cursor_prompt.md
docs/prompts/03_intake_api_cursor_prompt.md
docs/prompts/04_ai_classifier_cursor_prompt.md
docs/prompts/05_routing_engine_cursor_prompt.md
docs/prompts/06_bitrix24_adapter_cursor_prompt.md
docs/prompts/07_worker_pipeline_cursor_prompt.md
docs/prompts/08_admin_dashboard_cursor_prompt.md
docs/prompts/09_tests_security_cursor_prompt.md
docs/prompts/10_portfolio_packaging_cursor_prompt.md
```

Требования:

- `00_foundation_cursor_prompt.md` должен содержать этот полный prompt или его аккуратную версию.
- `01–10` должны быть draft prompts для будущей реализации.
- Каждый prompt должен содержать:
  - context;
  - source of truth;
  - task;
  - files to create/change;
  - non-goals;
  - acceptance criteria;
  - final report format.

Не реализуй EPIC 01–10 сейчас. Только подготовь prompt-файлы.

---

### 7. Создай checklists

Создай:

```text
docs/checklists/code_review_checklist.md
docs/checklists/security_checklist.md
docs/checklists/release_checklist.md
docs/checklists/portfolio_publication_checklist.md
```

#### `code_review_checklist.md`

Добавить пункты:

- scope соблюдён;
- нет лишних технологий;
- архитектура не нарушена;
- нет hardcoded secrets;
- нет unrelated changes;
- код читаемый;
- есть тесты;
- docs обновлены;
- acceptance criteria выполнены.

#### `security_checklist.md`

Добавить пункты:

- `.env` не в git;
- API keys не в коде;
- Bitrix24 webhook URL не в коде;
- PII не в demo data;
- logs masked;
- UI masked;
- screenshots masked;
- Basic Auth для admin planned/implemented;
- intake secret planned/implemented.

#### `release_checklist.md`

Добавить пункты:

- приложение запускается;
- tests green;
- README актуален;
- demo data работает;
- dashboard открывается;
- known issues описаны;
- release notes готовы.

#### `portfolio_publication_checklist.md`

Добавить пункты:

- нет секретов;
- нет `.env`;
- нет SQLite DB;
- нет logs;
- нет реальных данных;
- README содержит disclaimer;
- screenshots не содержат PII;
- GitHub/Notion/HH links checked.

---

### 8. Создай `.cursor/rules`

Создай:

```text
.cursor/rules/project_rules.md
.cursor/rules/python_fastapi_rules.md
.cursor/rules/testing_rules.md
.cursor/rules/security_rules.md
.cursor/rules/git_rules.md
```

#### `project_rules.md`

Включить:

- source of truth: `docs/ai_lead_intake_bitrix24_tz_v1_0.md`;
- не создавать новые версии ТЗ;
- не добавлять технологии вне scope без ADR;
- не менять архитектуру без ADR;
- перед кодом читать relevant EPIC;
- каждый этап завершать отчётом;
- не менять unrelated files.

#### `python_fastapi_rules.md`

Включить:

- Python 3.12;
- FastAPI;
- Pydantic;
- SQLAlchemy 2;
- config через pydantic-settings;
- separation of concerns:
  - API;
  - services;
  - integrations;
  - models;
  - utils.
- route handlers must not contain heavy business logic.

#### `testing_rules.md`

Включить:

- no real external network calls in tests;
- mock OpenAI;
- mock Bitrix24;
- unit tests for services;
- integration tests for pipeline;
- required edge cases.

#### `security_rules.md`

Включить:

- never commit `.env`;
- never commit webhook URL;
- never commit OpenAI API key;
- never use real PII;
- mask email/phone in logs/UI/screenshots;
- public repo checklist required before publication.

#### `git_rules.md`

Включить:

- branch strategy:
  - `main`;
  - `dev`;
  - `feature/<epic-name>`.
- commit convention:
  - `docs:`;
  - `chore:`;
  - `feat:`;
  - `fix:`;
  - `test:`;
  - `security:`;
  - `refactor:`.
- one epic = one branch;
- before merge: checklist + tests.

---

### 9. Создай `AGENTS.md`

Файл должен описывать:

- role of AI agent;
- source of truth;
- project scope;
- forbidden actions;
- coding rules;
- security rules;
- testing rules;
- documentation rules;
- uncertainty handling;
- final report format.

Обязательный final report format:

```markdown
## Done
- ...

## Files changed
- ...

## How to verify
- ...

## Notes / assumptions
- ...

## Next step
- ...
```

---

### 10. Создай `README.md` draft

README должен быть черновиком.

Минимальные разделы:

```markdown
# AI Lead Intake для Битрикс24

## Status

## What it is

## What it demonstrates

## Architecture

## Development approach

## Demo vs Production

## Documentation

## Roadmap

## Disclaimer
```

Обязательно указать:

```text
This is a demo/product prototype. It is not a commercial deployment.
Architecture is production-capable; first delivery is portfolio/demo MVP.
```

---

### 11. Создай `.gitignore`

Минимум:

```gitignore
# env
.env
.env.*
!.env.example

# python
__pycache__/
*.py[cod]
.pytest_cache/
.ruff_cache/
.mypy_cache/

# virtualenv
.venv/
venv/

# data
*.sqlite
*.sqlite3
*.db
data/
logs/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

---

## Acceptance criteria

EPIC 00 считается выполненным, если:

- создана структура `docs/`;
- создан `docs/project_brief.md`;
- создан `docs/architecture.md`;
- создан `docs/implementation_plan.md`;
- созданы все `docs/epics/*.md`;
- созданы все `docs/adr/*.md`;
- созданы все `docs/prompts/*.md`;
- созданы все `docs/checklists/*.md`;
- создан `AGENTS.md`;
- созданы `.cursor/rules/*.md`;
- создан `README.md` draft;
- создан `.gitignore`;
- нигде не создан функциональный код приложения;
- не создан `.env`;
- нет секретов;
- нет реальных персональных данных;
- нет SQLite DB;
- нет logs;
- все документы ссылаются на `docs/ai_lead_intake_bitrix24_tz_v1_0.md`;
- финальный отчёт содержит список файлов и следующий шаг.

---

## Definition of Done

Перед завершением проверь:

```text
[ ] Source of truth points to docs/ai_lead_intake_bitrix24_tz_v1_0.md
[ ] Docs structure created
[ ] Epics created
[ ] ADRs created
[ ] Cursor prompts created
[ ] Checklists created
[ ] .cursor/rules created
[ ] AGENTS.md created
[ ] README draft created
[ ] .gitignore created
[ ] No app runtime code created
[ ] No .env created
[ ] No secrets
[ ] No real PII
[ ] No DB/log files
[ ] Final report provided
```

---

## Final report

В конце ответа выведи:

```markdown
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
- EPIC 01 — Skeleton + Config + Healthcheck
```
