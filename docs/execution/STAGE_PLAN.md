# Stage plan: notify-gateway delivery

Цель: разложить путь к production-ready MVP на стадии, которые можно брать по очереди и дробить на атомарные таски.

## Общие правила исполнения стадий
- Каждая стадия имеет **Definition of Done (DoD)**.
- Пока DoD стадии не выполнен — следующую стадию не начинаем.
- Каждая задача в стадии должна иметь owner, оценку, статус и артефакт проверки.
- Результаты стадии фиксируются в `docs/execution/PROGRESS.md`.

---

## Stage 0 — Discovery & readiness baseline

### Цель
Подтвердить, что есть все входные данные и доступы для начала реализации и деплоя.

### Вход
- Доступный `YC_TOKEN`/IAM flow.
- Базовые cloud/folder IDs.

### Ключевые результаты
- Подтверждены cloud/folder/function/apigw/service-account контексты.
- Подтверждён доступ к Lockbox и список нужных ключей секрета.
- Зафиксирована карта «что берём из YC API / что берём из Lockbox / что храним в repo config».

### DoD
- [ ] Выполнен discovery-скрипт и сохранён результат в документации.
- [ ] Согласован минимальный набор IAM-ролей.
- [ ] Согласован список обязательных runtime env/secrets.

---

## Stage 1 — Repo hardening (foundation)

### Цель
Подготовить структуру репозитория и минимальный CI-контур для безопасной ежедневной разработки.

### Ключевые результаты
- Созданы каталоги `infra/env`, `infra/function/env`, `infra/scripts`, `.github/workflows`.
- Добавлены `*.env.example` шаблоны.
- Добавлен `ci.yml` (lint + tests).
- Обновлён runbook запуска тестов локально и в CI.

### DoD
- [ ] Структура каталогов создана.
- [ ] CI успешно проходит на PR.
- [ ] Нет секретов в git (проверка `.env`/токенов/ключей).

---

## Stage 2 — Deploy automation (main -> YC Function)

### Цель
Автоматизировать деплой из `main` в Yandex Cloud Function с подтягиванием runtime секретов из Lockbox.

### Ключевые результаты
- Реализованы скрипты:
  - `infra/scripts/yc_collect_context.sh`
  - `infra/scripts/yc_deploy_function.sh`
- Реализован workflow `.github/workflows/deploy.yml`.
- Поддержан `workflow_dispatch` и dry-run режим.

### DoD
- [ ] Workflow получает IAM token безопасным способом.
- [ ] Workflow читает секреты из Lockbox (без утечки в лог).
- [ ] Function обновляется автоматически на push в `main`.
- [ ] API Gateway обновляется/валидируется в пайплайне.

---

## Stage 3 — Runtime validation & observability

### Цель
Подтвердить корректность работы боевого контура после деплоя.

### Ключевые результаты
- Автоматический smoke-check `POST /notify`.
- Проверка доставки сообщения в Telegram технический чат.
- Минимальные operational checks (логи, коды ответов, rollback шаги).

### DoD
- [ ] Smoke-check встроен в deploy pipeline.
- [ ] Описан rollback-runbook.
- [ ] Зафиксированы SLO-lite критерии (например, доля успешных вызовов).

---

## Stage 4 — Production readiness

### Цель
Закрыть эксплуатационные риски и стабилизировать процесс релизов.

### Ключевые результаты
- Ротация ключей/секретов по регламенту.
- Проверки least privilege и аудит IAM.
- Полный DoD и handover документация.

### DoD
- [ ] Регламент ротации секретов описан и проверен.
- [ ] Минимизированы роли SA до необходимого набора.
- [ ] Документация on-call/ops актуальна.
