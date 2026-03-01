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

---

## 2026-02-28 — S3-T01

### Stage
Stage 3 — Runtime validation & observability.

### Done
- Добавлен `infra/scripts/smoke_notify.sh`.
- Реализовано:
  - `set -euo pipefail`;
  - обязательные env (`NOTIFY_ENDPOINT`, `NOTIFY_API_KEY`);
  - валидация HTTP-кода и JSON-ответа (`ok=true`, `telegram_message_id`);
  - безопасные режимы `--dry-run` и `--skip-send`.

### Blockers
- Нет.

### Next
- Выполнить S3-T02: встроить smoke-check в deploy pipeline.

---

## 2026-02-28 — S3-T02

### Stage
Stage 3 — Runtime validation & observability.

### Done
- Обновлён `.github/workflows/deploy.yml`:
  - добавлены env `YC_FUNCTION_ID` и `NOTIFY_ENDPOINT`.
  - в шаге валидации конфигурации добавлены проверки новых обязательных переменных.
  - добавлен шаг `Smoke-check /notify` с использованием `infra/scripts/smoke_notify.sh`.
- Падение smoke-check приводит к fail workflow.

### Blockers
- Нет.

### Next
- Выполнить S3-T03: уточнить rollback-runbook.

---

## 2026-02-28 — S3-T03

### Stage
Stage 3 — Runtime validation & observability.

### Done
- Обновлён `docs/DEPLOY_RUNBOOK.md`:
  - добавлены operational trigger-criteria rollback;
  - описаны function/API gateway rollback шаги;
  - добавлена пост-rollback верификация.

### Blockers
- Нет.

### Next
- Выполнить S3-T04: зафиксировать SLO-lite и operational checks.

---

## 2026-02-28 — S3-T04

### Stage
Stage 3 — Runtime validation & observability.

### Done
- Добавлен `docs/SLO_AND_OBSERVABILITY.md`.
- Зафиксированы:
  - SLO-lite критерии;
  - post-deploy и ежедневные operational checks;
  - источники наблюдаемости;
  - триггеры эскалации и команды triage.

### Blockers
- Нет.

### Next
- Закрыть Stage 3 и перейти к Stage 4.

---

## 2026-02-28 — Stage 3 complete / transition

### Stage
Stage 3 — Runtime validation & observability ✅ завершена.

### Done
- Все задачи S3-T01…S3-T04 закрыты.
- Definition of Done Stage 3 выполнен:
  - smoke-check реализован и встроен в deploy pipeline;
  - rollback-runbook расширен операционными шагами;
  - SLO-lite и observability checks зафиксированы.
- `CURRENT_STAGE_TASKS.md` переключён на Stage 4 и заполнен первым набором атомарных задач.

### Blockers
- Нет.

### Next
Первый набор атомарных задач для **Stage 4 — Production readiness**:
1. **S4-T01** Регламент ротации секретов.
2. **S4-T02** Матрица IAM least privilege.
3. **S4-T03** On-call/ops playbook и эскалации.

---

## 2026-02-28 — S4-T01

### Stage
Stage 4 — Production readiness.

### Done
- Добавлен `docs/SECRET_ROTATION.md`.
- Зафиксированы scope секретов, периодичность ротации, пошаговый процесс, emergency-режим и checklist верификации после ротации.

### Blockers
- Нет.

### Next
- Выполнить S4-T02: подготовить IAM least-privilege матрицу.

---

## 2026-02-28 — S4-T02

### Stage
Stage 4 — Production readiness.

### Done
- Добавлен `docs/IAM_LEAST_PRIVILEGE.md`.
- Зафиксирован текущий baseline ролей и целевая least-privilege матрица для deploy SA, integration SA и read-only наблюдаемости.
- Добавлен checklist hardening/acceptance после ужесточения прав.

### Blockers
- Нет.

### Next
- Выполнить S4-T03: обновить on-call/ops playbook.

---

## 2026-02-28 — S4-T03

### Stage
Stage 4 — Production readiness.

### Done
- Добавлен `docs/ONCALL_OPS_PLAYBOOK.md`.
- Описаны каналы эскалации, SLA реакции, triage checklist и playbook по типовым инцидентам (smoke-check fail, 401/403, 5xx/Telegram errors).

### Blockers
- Нет.

### Next
- Закрыть Stage 4 и зафиксировать итоговый статус программы.

---

## 2026-02-28 — Stage 4 complete / program complete

### Stage
Stage 4 — Production readiness ✅ завершена.

### Done
- Все задачи S4-T01…S4-T03 закрыты.
- Definition of Done Stage 4 выполнен:
  - регламент ротации секретов оформлен;
  - least-privilege IAM матрица сформирована;
  - on-call/ops playbook зафиксирован.
- Все стадии Stage 0..4 отмечены закрытыми в execution-трекере.

### Blockers
- Нет.

### Next
- Поддерживающий режим: выполнять только change-requests и актуализацию runbook/политик по мере изменений инфраструктуры.

---

## 2026-02-28 — S4-T04 (maintenance): deploy env alias compatibility

### Stage
Stage 4 — Production readiness (maintenance mode).

### Done
- В `.github/workflows/deploy.yml` добавлена поддержка alias переменной `YC_CLOUD_FUNCTION_NAME`:
  - если `YC_FUNCTION_NAME` не задан, workflow автоматически использует `YC_CLOUD_FUNCTION_NAME`;
  - валидация выводит явную подсказку про оба имени переменной.
- Документация синхронизирована:
  - `docs/DEPLOY_RUNBOOK.md` обновлён с указанием alias;
  - `docs/ENV_AND_ACCESS.md` обновлён с примечанием по fallback-переменной.
- `docs/execution/CURRENT_STAGE_TASKS.md` пополнен задачей S4-T04 как завершённой.

### Blockers
- Нет.

### Next
- Проверить фактический запуск deploy workflow в CI с переменными из окружения `CODEX_DEV`.

---

## 2026-02-28 — S4-T05 (maintenance): bootstrap missing gateway/env vars

### Stage
Stage 4 — Production readiness (maintenance mode).

### Done
- Добавлен скрипт `infra/scripts/yc_bootstrap_notify_endpoint.sh`:
  - рендерит `infra/apigw.yaml` с `YC_FUNCTION_ID` и `YC_SERVICE_ACCOUNT_ID`;
  - создаёт/обновляет API Gateway по имени `YC_API_GW_NAME` (default `notify-gateway-gw`);
  - вычисляет и печатает `NOTIFY_ENDPOINT` (`https://<gateway-domain>/notify`);
  - опционально синхронизирует `YC_API_GW_NAME` и `NOTIFY_ENDPOINT` в Yandex Lockbox (`LOCKBOX_SECRET_ID` или `LOCKBOX_SECRET_NAME`).
- `docs/DEPLOY_RUNBOOK.md` дополнен разделом bootstrap для автоматического восстановления `YC_API_GW_NAME` и `NOTIFY_ENDPOINT`.

### Blockers
- Нет.

### Next
- Проверить deploy workflow в GitHub Actions после обновления env/Lockbox.

---

## 2026-02-28 — S4-T06 (maintenance): deploy fix for missing rg on runner

### Stage
Stage 4 — Production readiness (maintenance mode).

### Done
- Исправлен `infra/scripts/yc_bootstrap_notify_endpoint.sh`, чтобы деплой не требовал `rg` на runner:
  - проверка неразрешённых плейсхолдеров переведена с `rg -q` на `grep -q`;
  - удалена обязательная проверка `require_cmd rg`.
- Это устраняет падение шага `Apply API Gateway spec and resolve endpoint` с ошибкой `required command 'rg' is not installed`.

### Blockers
- Нет.

### Next
- Перезапустить GitHub Actions deploy и убедиться, что bootstrap + smoke-check проходят на `ubuntu-latest`.
## 2026-02-28 — S4-T07

### Stage
Stage 4 — Production readiness.

### Done
- Добавлена поддержка публичного домена API через переменную `NOTIFY_PUBLIC_BASE_URL` в `infra/scripts/yc_bootstrap_notify_endpoint.sh`.
- Логика bootstrap обновлена: при заданном `NOTIFY_PUBLIC_BASE_URL` endpoint формируется как `<base>/notify`.
- В `.github/workflows/deploy.yml` добавлен env `NOTIFY_PUBLIC_BASE_URL` (vars/secrets) для smoke-check/Lockbox.
- Обновлён `docs/DEPLOY_RUNBOOK.md` с инструкцией по привязке домена (`api.<domain>`) и настройке переменных.

### Blockers
- Нет.

### Next
- Применить DNS-запись `api.<domain>` и задать `NOTIFY_PUBLIC_BASE_URL` в GitHub Environment `production`.

---

## 2026-02-28 — Documentation sync audit

### Stage
Stage 4 — Production readiness (maintenance mode).

### Done
- Проведена сверка фактической реализации (workflow + infra scripts) и документации.
- Исправлены рассинхроны:
  - `docs/execution/CURRENT_STAGE_TASKS.md` очищен от конфликтующих секций Stage 3/4, статус приведён к maintenance mode;
  - `docs/DEPLOY_RUNBOOK.md` переписан без дублей и синхронизирован с актуальным `.github/workflows/deploy.yml`;
  - `docs/STATUS.md` обновлён под текущее состояние (Stage 0..4 завершены);
  - `docs/PLAN.md` обновлён в формате «план + факт выполнения».

### Blockers
- `git fetch origin && git rebase origin/main` недоступны в текущем контейнере, так как remote `origin` не настроен.
- Владелец: владелец проекта/CI окружения.
- Действия для снятия:
  1. Добавить корректный remote `origin` в локальный clone.
  2. Проверить доступ к `origin/main` (`git fetch origin`).
- Критерий снятия: команда `git fetch origin` выполняется без ошибки.

### Next
- Поддерживать синхронизацию docs при каждом изменении deploy workflow/infra scripts.

---

## 2026-02-28 — Maintenance backlog reprioritization (deploy fix first)

### Stage
Stage 4 — Production readiness (maintenance mode).

### Done
- Пересобран и актуализирован backlog в `docs/execution/CURRENT_STAGE_TASKS.md` по новым product-request.
- Введён приоритет задач:
  1. `S4-T08 (P0)` — исправление деплоя: убрать зависимость от установки YC CLI в GitHub Actions при сохранении функциональности.
  2. `S4-T09..S4-T11 (P1)` — шаблоны сообщений, выбор чата (id/alias), help-режим API.
  3. `S4-T12 (P2)` — расширенный backlog полезных улучшений v2.
- Зафиксированы критерии приёмки и артефакты проверки для всех новых задач.

### Blockers
- `git fetch origin && git rebase origin/main` недоступны в текущем контейнере, так как remote `origin` не настроен.
- Владелец: владелец проекта/CI окружения.
- Действия для снятия:
  1. Добавить корректный remote `origin` в локальный clone.
  2. Проверить доступ к `origin/main` (`git fetch origin`).
- Критерий снятия: команда `git fetch origin` выполняется без ошибки.

### Next
- Взять в `in_progress` задачу `S4-T08 (P0)` и выполнить рефактор deploy workflow без YC CLI.
