# notify-gateway — план старта цикла разработки

> Цель: перейти от «доступ есть» к контролируемой реализации и деплою в Yandex Cloud с автоматическим сбором env/secrets из Lockbox.

## 1) Что именно нужно для проекта (data contract инфраструктуры)

Ниже — обязательный минимальный набор данных для MVP и их источник.

### 1.1 Инфраструктурный контекст
- `YC_CLOUD_ID` — ID облака.
- `YC_FOLDER_ID` — ID рабочей папки.
- `YC_SERVICE_ACCOUNT_ID` — SA для CI/CD-деплоя.
- `YC_FUNCTION_NAME` / `YC_FUNCTION_ID` — целевая Cloud Function.
- `YC_API_GW_NAME` / `YC_API_GW_ID` — целевой API Gateway.

### 1.2 Runtime-конфигурация функции
- `NOTIFY_MAX_MESSAGE_LEN` (опционально).
- `NOTIFY_MAX_EXTRA_LEN` (опционально).
- `LOG_LEVEL` (опционально).

### 1.3 Runtime-секреты
- `NOTIFY_API_KEYS`.
- `TELEGRAM_BOT_TOKEN`.
- `TELEGRAM_CHAT_ID`.

---

## 2) Где берём данные: YC API vs Lockbox

## 2.1 Получаем из YC API (автодискавери)
- Cloud/Folder: Resource Manager API.
- Service Accounts: IAM API.
- Functions: Serverless Functions API.
- API Gateways: API Gateway API.
- Сервисные привязки/роли (проверка): IAM policy/list access bindings.

## 2.2 Получаем из Lockbox
- Все runtime-секреты функции: `NOTIFY_API_KEYS`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`.
- Опционально — deploy secrets, если не используем OIDC/short-lived IAM в CI.

## 2.3 Решение по источнику правды
- **Source of truth для секретов:** Lockbox.
- **Source of truth для инфраструктурных ID:** repo-level config (`infra/env/*.env`) + сверка через YC API.
- **Source of truth для runtime non-secret config:** repo (`infra/function/env/*.env`).

---

## 3) Проверка полноты доступа (готовность к реализации)

## 3.1 Чеклист доступов
- [ ] CI service account имеет роли: `serverless.functions.editor`, `api-gateway.editor`, `iam.serviceAccounts.user`.
- [ ] API Gateway integration SA имеет `serverless.functions.invoker` на функцию.
- [ ] Есть доступ к Lockbox: чтение payload секрета(ов) для деплоя.

## 3.2 Чеклист извлечения данных
- [ ] Автодискавери cloud/folder выполняется.
- [ ] Видим целевую функцию и API Gateway (или можем создать).
- [ ] Читаем Lockbox secret payload с нужными ключами.
- [ ] Нет ручного ввода секретов в workflow.

---

## 4) Подготовка структуры репозитория

Предлагаемая целевая структура:

```text
.
├── src/
├── tests/
├── infra/
│   ├── apigw.yaml
│   ├── env/
│   │   ├── dev.env.example
│   │   └── prod.env.example
│   ├── function/
│   │   └── env/
│   │       ├── common.env.example
│   │       └── prod.env.example
│   └── scripts/
│       ├── yc_discovery_via_api.sh
│       ├── yc_collect_context.sh
│       └── yc_deploy_function.sh
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
└── docs/
```

### Принципы
- `*.example` храним в git, реальные значения — только в Lockbox/GitHub Secrets.
- Скрипты в `infra/scripts/` идемпотентные, с `set -euo pipefail`.
- Любой deploy-скрипт должен поддерживать режим `--dry-run`.

---

## 5) План для тестов (чтобы разработку можно было запускать сразу)

## 5.1 Локальные тесты
- Unit: `pytest -q` (валидаторы, авторизация, формирование payload в Telegram).
- Contract tests: проверка схемы входного JSON и формата ответов.

## 5.2 CI тесты
- На PR: линтер + unit tests + (опц.) coverage threshold.
- На `main`: тот же набор + подготовка deploy-артефакта (zip функции).

## 5.3 Smoke после деплоя
- `POST /notify` с тестовым ключом в технический чат.
- Проверка response-кода и факта доставки в Telegram.

---

## 6) План GitHub Actions для деплоя main → Yandex Function

## 6.1 Триггер
- `push` в `main`.
- `workflow_dispatch` для ручного запуска.

## 6.2 Что workflow делает
1. Получает короткоживущий IAM token (через OAuth secret или OIDC flow).
2. Через Lockbox API читает секрет(ы) runtime.
3. Собирает runtime env файл в памяти runner (без записи секретов в лог).
4. Упаковывает функцию в zip.
5. Обновляет/создаёт Cloud Function.
6. Обновляет API Gateway (если требуется, через `infra/apigw.yaml`).
7. Выполняет smoke-check endpoint.

## 6.3 Минимальные секреты GitHub
- `YC_TOKEN` **или** безопасный механизм выдачи IAM token.
- `YC_CLOUD_ID`, `YC_FOLDER_ID`.
- `YC_SERVICE_ACCOUNT_ID` (если нужно в скриптах).
- `YC_LOCKBOX_SECRET_ID` (или набор secret IDs).

## 6.4 Требования безопасности
- Маскировка секретов (`::add-mask::`).
- `set -x` запрещён в шагах, где могут всплыть секреты.
- Принцип least privilege для SA.

---

## 7) Итерационный roadmap

### Итерация 0 (сейчас): Discovery + планирование
- [x] Подтвердить доступ к YC API из runtime.
- [x] Зафиксировать стратегию получения данных и секретов.
- [x] Сформировать план структуры репозитория и CI/CD.

### Итерация 1: Repo hardening
- [ ] Ввести целевую структуру `infra/`, `.github/workflows/`, `*.example`.
- [ ] Добавить `ci.yml` (линт + тесты).

### Итерация 2: Deploy automation
- [ ] Добавить `infra/scripts/yc_collect_context.sh`.
- [ ] Добавить `infra/scripts/yc_deploy_function.sh`.
- [ ] Добавить `deploy.yml` с чтением Lockbox и деплоем в Function.

### Итерация 3: Validation
- [ ] Smoke-check после деплоя.
- [ ] Runbook rollback (предыдущая версия функции).
- [ ] Финализация DoD для production.

---

## 8) Definition of Ready для начала активной разработки

Реализацию фич начинаем, когда:
- [ ] Заполнены IDs ресурсов (`cloud/folder/function/apigw/SA`).
- [ ] Проверено чтение всех нужных секретов из Lockbox.
- [ ] Подготовлен и согласован deploy workflow (черновик `deploy.yml`).
- [ ] `pytest -q` стабильно проходит в CI.
