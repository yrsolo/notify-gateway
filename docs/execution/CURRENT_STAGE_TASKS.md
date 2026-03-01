# Current stage tasks

Текущая стадия: **Stage 4 — Production readiness (maintenance mode)**.

> Формат: ID / описание / owner / оценка / критерии приёмки / артефакт проверки / статус.

## Stage 4 completed baseline

- [x] **S4-T01** Описать регламент ротации секретов и расписание.
  - Owner: agent
  - Оценка: 0.5d
  - Артефакт проверки: `docs/SECRET_ROTATION.md`.
  - Статус: `done`

- [x] **S4-T02** Провести ревизию IAM ролей и предложить least-privilege матрицу.
  - Owner: agent
  - Оценка: 0.5d
  - Артефакт проверки: `docs/IAM_LEAST_PRIVILEGE.md`.
  - Статус: `done`

- [x] **S4-T03** Обновить on-call/ops документацию и runbook инцидентов.
  - Owner: agent
  - Оценка: 0.5d
  - Артефакт проверки: `docs/ONCALL_OPS_PLAYBOOK.md`.
  - Статус: `done`

- [x] **S4-T04** Добавить совместимость с alias `YC_CLOUD_FUNCTION_NAME` для deploy workflow.
  - Owner: agent
  - Оценка: 0.25d
  - Артефакт проверки: `.github/workflows/deploy.yml`.
  - Статус: `done`

- [x] **S4-T05** Добавить bootstrap-скрипт для восстановления `YC_API_GW_NAME` и `NOTIFY_ENDPOINT`.
  - Owner: agent
  - Оценка: 0.5d
  - Артефакт проверки: `infra/scripts/yc_bootstrap_notify_endpoint.sh`, `docs/DEPLOY_RUNBOOK.md`.
  - Статус: `done`

- [x] **S4-T06** Убрать hard-dependency от `rg` в bootstrap API Gateway.
  - Owner: agent
  - Оценка: 0.25d
  - Артефакт проверки: `infra/scripts/yc_bootstrap_notify_endpoint.sh`.
  - Статус: `done`

- [x] **S4-T07** Поддержать публичный домен API в bootstrap/deploy.
  - Owner: agent
  - Оценка: 0.25d
  - Артефакт проверки: `infra/scripts/yc_bootstrap_notify_endpoint.sh`, `.github/workflows/deploy.yml`, `docs/DEPLOY_RUNBOOK.md`.
  - Статус: `done`

## Maintenance backlog (приоритет: исправление деплоя)

- [ ] **S4-T08 (P0)** Убрать установку YC CLI из deploy workflow и сохранить функциональность через API/скрипты.
  - Owner: agent
  - Оценка: 1d
  - Критерии приёмки:
    1. В `.github/workflows/deploy.yml` удалены шаги установки/конфигурации `yc` CLI.
    2. Разрешение Function/Gateway контекста выполняется без `yc` binary.
    3. Dry-run deploy workflow проходит без YC CLI.
  - Артефакт проверки: `.github/workflows/deploy.yml`, `infra/scripts/*.sh`, CI logs.
  - Статус: `planned`

- [ ] **S4-T09 (P1)** Добавить шаблоны сообщений `notification`, `error`, `raw`.
  - Owner: agent
  - Оценка: 1d
  - Критерии приёмки:
    1. Поддержаны 3 шаблона в `POST /notify`.
    2. Для `notification`/`error` в сообщении есть проект, дата/время, текст и служебные поля.
    3. Для `raw` отправляется только исходный текст.
  - Артефакт проверки: `src/handler.py`, `tests/test_handler.py`, `README.md`.
  - Статус: `planned`

- [ ] **S4-T10 (P1)** Добавить опциональную отправку в другой чат (`chat_id` или alias `chat`).
  - Owner: agent
  - Оценка: 0.75d
  - Критерии приёмки:
    1. Поддержан payload override через `chat_id`.
    2. Поддержан alias через env-мапу (`TELEGRAM_CHAT_ALIASES_JSON`).
    3. Добавлены тесты на дефолтный чат, override и невалидный alias.
  - Артефакт проверки: `src/handler.py`, `tests/test_handler.py`, `infra/function/env/*.env.example`, `README.md`.
  - Статус: `planned`

- [ ] **S4-T11 (P1)** Добавить help-режим API (`/help`, `/?`, пустой запрос).
  - Owner: agent
  - Оценка: 0.5d
  - Критерии приёмки:
    1. API возвращает справку с поддерживаемыми шаблонами и примерами payload.
    2. Описаны поля, валидация и маршрутизация по чатам.
    3. Добавлены тесты help-режима.
  - Артефакт проверки: `src/handler.py`, `tests/test_handler.py`, `README.md`, `infra/apigw.yaml` (при необходимости).
  - Статус: `planned`

- [ ] **S4-T12 (P2)** Сформировать backlog полезных улучшений v2 и критерии приоритезации.
  - Owner: agent
  - Оценка: 0.5d
  - Критерии приёмки:
    1. Зафиксированы эпики reliability/observability/security.
    2. Для каждого эпика указаны оценка, риск, зависимость и owner.
  - Артефакт проверки: `docs/PLAN.md` (или отдельный `docs/ROADMAP_V2.md`).
  - Статус: `planned`

## Program status
- Все стадии `Stage 0..4` закрыты по execution-трекеру.
- Репозиторий в maintenance mode, новые change-requests исполняются как атомарные задачи Stage 4.

## WIP limit
- Одновременно в `in_progress` не более 2 задач.
- Текущее состояние: 0 `in_progress`.
