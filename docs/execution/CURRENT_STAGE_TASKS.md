# Current stage tasks

Текущая стадия: **Stage 4 — Production readiness**.

> Формат: ID / описание / owner / оценка / критерии приёмки / артефакт проверки / статус.

## Stage 4 backlog (атомарные задачи)

- [x] **S4-T01** Описать регламент ротации секретов и расписание.
  - Owner: agent
  - Оценка: 0.5d
  - Критерии приёмки:
    1. Документированы scope, периодичность и шаги ротации.
    2. Есть checklist верификации после ротации.
  - Артефакт проверки: `docs/SECRET_ROTATION.md`.
  - Статус: `done`

- [x] **S4-T02** Провести ревизию IAM ролей и предложить least-privilege матрицу.
  - Owner: agent
  - Оценка: 0.5d
  - Критерии приёмки:
    1. Зафиксирован текущий набор ролей.
    2. Сформирована целевая минимальная матрица ролей.
  - Артефакт проверки: `docs/IAM_LEAST_PRIVILEGE.md`.
  - Статус: `done`

- [x] **S4-T03** Обновить on-call/ops документацию и runbook инцидентов.
  - Owner: agent
  - Оценка: 0.5d
  - Критерии приёмки:
    1. Описаны каналы эскалации и SLA реакции.
    2. Есть playbook по типовым инцидентам.
  - Артефакт проверки: `docs/ONCALL_OPS_PLAYBOOK.md`.
  - Статус: `done`

- [x] **S4-T04** Добавить совместимость с alias `YC_CLOUD_FUNCTION_NAME` для deploy workflow.
  - Owner: agent
  - Оценка: 0.25d
  - Критерии приёмки:
    1. Workflow принимает `YC_FUNCTION_NAME` или alias `YC_CLOUD_FUNCTION_NAME`.
    2. Ошибка валидации подсказывает корректные имена переменных.
  - Артефакт проверки: `.github/workflows/deploy.yml`.
  - Статус: `done`


- [x] **S4-T06** Убрать hard-dependency от `rg` в bootstrap API Gateway.
  - Owner: agent
  - Оценка: 0.25d
  - Критерии приёмки:
    1. Скрипт bootstrap не требует установленный `rg` на GitHub runner.
    2. Проверка плейсхолдеров выполняется стандартным POSIX/Ubuntu инструментом.
  - Артефакт проверки: `infra/scripts/yc_bootstrap_notify_endpoint.sh`.
  - Статус: `done`


- [x] **S4-T07** Поддержать публичный домен API в bootstrap/deploy.
  - Owner: agent
  - Оценка: 0.25d
  - Критерии приёмки:
    1. Bootstrap-скрипт поддерживает override endpoint через переменную окружения.
    2. Deploy workflow прокидывает переменную публичного base URL.
    3. Runbook описывает настройку домена и переменных.
  - Артефакт проверки: `infra/scripts/yc_bootstrap_notify_endpoint.sh`, `.github/workflows/deploy.yml`, `docs/DEPLOY_RUNBOOK.md`.
  - Статус: `done`

Текущая стадия: **Stage 3 — Runtime validation & observability**.

> Формат: ID / описание / owner / оценка / критерии приёмки / артефакт проверки / статус.

## Stage 2 completion snapshot

- [x] S2-T01 `yc_collect_context.sh`
- [x] S2-T02 `yc_deploy_function.sh`
- [x] S2-T03 `.github/workflows/deploy.yml`
- [x] S2-T04 API Gateway apply/validate step (`yc_apply_apigw.sh` + workflow)
- [x] S2-T05 Deploy runbook + rollback docs

Stage 2 DoD: **выполнен**.

## Stage 3 backlog (атомарные задачи)

- [ ] **S3-T01** Добавить smoke-check скрипт для `POST /notify`.
  - Owner: agent
  - Оценка: 0.5d
  - Критерии приёмки:
    1. Есть скрипт `infra/scripts/smoke_notify.sh` с `set -euo pipefail`.
    2. Скрипт валидирует HTTP-код и формат JSON ответа.
    3. Поддержан безопасный dry-run/skip-send режим.
  - Артефакт проверки: `bash -n infra/scripts/smoke_notify.sh` + dry-run вывод.
  - Статус: `todo`

- [ ] **S3-T02** Встроить smoke-check в deploy pipeline.
  - Owner: agent
  - Оценка: 0.5d
  - Критерии приёмки:
    1. После деплоя запускается smoke-check.
    2. Падение smoke-check фейлит workflow.
  - Артефакт проверки: `.github/workflows/deploy.yml`.
  - Статус: `todo`

- [ ] **S3-T03** Документировать rollback-runbook с операционными шагами.
  - Owner: agent
  - Оценка: 0.5d
  - Критерии приёмки:
    1. Описан rollback функции и gateway.
    2. Описаны проверки после rollback.
  - Артефакт проверки: `docs/DEPLOY_RUNBOOK.md`.
  - Статус: `todo`

- [ ] **S3-T04** Зафиксировать SLO-lite и operational checks.
  - Owner: agent
  - Оценка: 0.5d
  - Критерии приёмки:
    1. Описаны критерии успешности (например, доля 2xx smoke-check).
    2. Описаны источники логов и триггеры эскалации.
  - Артефакт проверки: новый документ в `docs/`.
  - Статус: `todo`

## WIP limit
- Одновременно в `in_progress` не более 2 задач.
- Текущее состояние: 0 `in_progress`.

## Definition of Done for Stage 4
- [x] S4-T01 завершена
- [x] S4-T02 завершена
- [x] S4-T03 завершена
- [x] S4-T04 завершена
- [x] S4-T06 завершена
- [x] S4-T07 завершена

## Program status
- Все стадии `Stage 0..4` закрыты по execution-трекеру.

## Definition of Done for Stage 3
- [ ] S3-T01 завершена
- [ ] S3-T02 завершена
- [ ] S3-T03 завершена
- [ ] S3-T04 завершена