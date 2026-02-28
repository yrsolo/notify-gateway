# Execution progress log

Формат записи:
- Дата
- Стадия
- Что сделано
- Что заблокировано
- Следующий шаг

---

## 2026-02-28 — S1-T01

### Stage
Stage 1 — Repo hardening (foundation).

### Done
- Определена текущая активная стадия по `STAGE_PLAN.md`, `CURRENT_STAGE_TASKS.md`, `PROGRESS.md`.
- Уточнён backlog Stage 1 до атомарного формата (owner/оценка/критерии/артефакты).
- Созданы каталоги `infra/env`, `infra/function/env`, `infra/scripts`, `.github/workflows`.

### Blockers
- Нет.

### Next
- Выполнить S1-T02: добавить env-шаблоны без секретов.

---

## 2026-02-28 — S1-T02

### Stage
Stage 1 — Repo hardening (foundation).

### Done
- Добавлены env-шаблоны:
  - `infra/env/dev.env.example`
  - `infra/env/prod.env.example`
  - `infra/function/env/common.env.example`
  - `infra/function/env/prod.env.example`
- Подтверждено, что в git не добавлены реальные `.env`/секреты.

### Blockers
- Нет.

### Next
- Выполнить S1-T03: добавить PR CI workflow с lint + tests.

---

## 2026-02-28 — S1-T03

### Stage
Stage 1 — Repo hardening (foundation).

### Done
- Добавлен `.github/workflows/ci.yml`.
- Workflow запускается на `pull_request`/`workflow_dispatch`.
- В workflow добавлены шаги `ruff check .` и `pytest -q`.

### Blockers
- Нет.

### Next
- Выполнить S1-T04: документировать security guardrails CI.

---

## 2026-02-28 — S1-T04

### Stage
Stage 1 — Repo hardening (foundation).

### Done
- Добавлен документ `docs/security/CI_GUARDRAILS.md`.
- Зафиксированы правила: не логировать секреты, не использовать `set -x` в секретных шагах, использовать `set -euo pipefail` в infra-скриптах.

### Blockers
- Нет.

### Next
- Выполнить S1-T05: обновить runbook локального запуска.

---

## 2026-02-28 — S1-T05

### Stage
Stage 1 — Repo hardening (foundation).

### Done
- Обновлён `README.md`:
  - добавлен runbook локальных проверок;
  - добавлены ссылки на env-шаблоны и CI workflow;
  - добавлена ссылка на CI security guardrails.
- Выполнены релевантные проверки локально: `ruff check .`, `pytest -q`.

### Blockers
- Нет.

### Next
- Закрыть Stage 1 и зафиксировать переход к Stage 2.

---

## 2026-02-28 — Stage 1 complete / transition

### Stage
Stage 1 — Repo hardening (foundation) ✅ завершена.

### Done
- Все задачи S1-T01…S1-T05 закрыты.
- Definition of Done Stage 1 выполнен полностью.
- Подготовлен переход к Stage 2 — Deploy automation.

### Blockers
- Нет.

### Next
Первый набор атомарных задач для **Stage 2 — Deploy automation**:
1. **S2-T01** Создать `infra/scripts/yc_collect_context.sh` с `set -euo pipefail`, проверкой обязательных env и dry-run.
2. **S2-T02** Создать `infra/scripts/yc_deploy_function.sh` с dry-run и безопасной обработкой секретов (без вывода в лог).
3. **S2-T03** Добавить `.github/workflows/deploy.yml` (`push main` + `workflow_dispatch`) с безопасным получением IAM token.
4. **S2-T04** Добавить pipeline-шаг валидации/обновления API Gateway (`infra/apigw.yaml`).
5. **S2-T05** Документировать deploy-runbook и rollback в `docs/`.
