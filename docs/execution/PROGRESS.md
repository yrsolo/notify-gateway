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

---

## 2026-02-28 — Stage 2 kickoff

### Stage
Stage 2 — Deploy automation (main -> YC Function).

### Done
- Переключен `CURRENT_STAGE_TASKS.md` на Stage 2.
- Backlog Stage 2 зафиксирован в атомарном формате с критериями и артефактами проверки.

### Blockers
- Нет.

### Next
- Выполнить S2-T01: добавить `infra/scripts/yc_collect_context.sh`.

---

## 2026-02-28 — S2-T01

### Stage
Stage 2 — Deploy automation (main -> YC Function).

### Done
- Добавлен `infra/scripts/yc_collect_context.sh`.
- В скрипте реализовано:
  - `set -euo pipefail`;
  - проверка обязательных env (`YC_FOLDER_ID`, `YC_TOKEN|YC_IAM_TOKEN`);
  - режим `--dry-run` без сетевых вызовов;
  - маскирование IAM token в выводе.
- Скрипт сделан исполняемым (`chmod +x`).

### Blockers
- Нет.

### Next
- Выполнить S2-T02: добавить `infra/scripts/yc_deploy_function.sh`.

---

## 2026-02-28 — S2-T02

### Stage
Stage 2 — Deploy automation (main -> YC Function).

### Done
- Добавлен `infra/scripts/yc_deploy_function.sh`.
- В скрипте реализовано:
  - `set -euo pipefail`;
  - обязательная валидация env (`YC_FOLDER_ID`, `YC_FUNCTION_NAME`);
  - режим `--dry-run` без вызовов `yc`/сети;
  - create/update логика функции по имени;
  - формирование новой версии функции с runtime/entrypoint/resource параметрами;
  - безопасная обработка env/secrets ссылок без вывода секретных значений.

### Blockers
- Нет.

### Next
- Выполнить S2-T03: добавить `.github/workflows/deploy.yml`.

---

## 2026-02-28 — S2-T03

### Stage
Stage 2 — Deploy automation (main -> YC Function).

### Done
- Добавлен `.github/workflows/deploy.yml`.
- Workflow запускается на `push` в `main` и `workflow_dispatch`.
- Добавлено безопасное получение IAM token:
  - приоритет `YC_IAM_TOKEN`;
  - fallback обмен `YC_TOKEN -> iamToken`;
  - маскирование токена через `::add-mask::`;
  - без вывода секретов в лог.
- Workflow использует скрипты из `infra/scripts` для discovery/deploy.

### Blockers
- Нет.

### Next
- Выполнить S2-T04: добавить шаг валидации/обновления API Gateway.

---

## 2026-02-28 — S2-T04

### Stage
Stage 2 — Deploy automation (main -> YC Function).

### Done
- Добавлен `infra/scripts/yc_apply_apigw.sh` для валидации/применения `infra/apigw.yaml`.
- Реализовано:
  - `set -euo pipefail`;
  - валидация обязательных env (`YC_FOLDER_ID`, `YC_API_GW_NAME`, `YC_FUNCTION_ID`, `YC_SERVICE_ACCOUNT_ID`);
  - рендер шаблона с заменой placeholder-ов;
  - проверка отсутствия незаменённых `<YOUR_...>`;
  - create/update API Gateway по имени;
  - `--dry-run` режим.
- В deploy workflow добавлен отдельный шаг `Apply API Gateway spec`.

### Blockers
- Нет.

### Next
- Выполнить S2-T05: документировать deploy-runbook и rollback.

---

## 2026-02-28 — S2-T05

### Stage
Stage 2 — Deploy automation (main -> YC Function).

### Done
- Добавлен `docs/DEPLOY_RUNBOOK.md`.
- Описаны:
  - required env/secrets для deploy workflow;
  - пошаговый процесс деплоя;
  - локальный dry-run;
  - rollback для Function и API Gateway;
  - требования по безопасному логированию секретов.
- `README.md` дополнен ссылкой на deploy runbook.

### Blockers
- Нет.

### Next
- Закрыть Stage 2 и перейти к Stage 3.

---

## 2026-02-28 — Stage 2 complete / transition

### Stage
Stage 2 — Deploy automation (main -> YC Function) ✅ завершена.

### Done
- Все задачи S2-T01…S2-T05 закрыты.
- Definition of Done Stage 2 выполнен:
  - безопасная подготовка IAM token в workflow;
  - поддержка dry-run;
  - автоматизация деплоя функции;
  - валидация/обновление API Gateway;
  - документирован deploy/rollback runbook.
- `CURRENT_STAGE_TASKS.md` переключён на Stage 3 и заполнен первым набором атомарных задач.

### Blockers
- Нет.

### Next
Первый набор атомарных задач для **Stage 3 — Runtime validation & observability**:
1. **S3-T01** Скрипт smoke-check `POST /notify`.
2. **S3-T02** Интеграция smoke-check в deploy workflow.
3. **S3-T03** Уточнение rollback-runbook под операционное применение.
4. **S3-T04** Формализация SLO-lite и operational checks.
