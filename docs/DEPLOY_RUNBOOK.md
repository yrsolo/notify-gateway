# Deploy runbook (Stage 3)

Документ описывает безопасный деплой `notify-gateway`, smoke-check и rollback-процедуры.
# Deploy runbook (Stage 2)

Документ описывает безопасный деплой `notify-gateway` в Yandex Cloud Function и обновление API Gateway.

## 1) Требуемые переменные и секреты

### GitHub Actions Variables (non-secret)
- `YC_FOLDER_ID`
- `YC_FUNCTION_NAME` (или `YC_CLOUD_FUNCTION_NAME` как alias)
- `YC_FUNCTION_ID`
- `YC_API_GW_NAME`
- `YC_SERVICE_ACCOUNT_ID`
- `NOTIFY_ENDPOINT` (полный URL для `POST /notify`)
- `NOTIFY_PUBLIC_BASE_URL` (опционально, например `https://api.solofarm.ru`; если задан, используется как публичный endpoint для smoke-check и записи в Lockbox)

### GitHub Actions Secrets
- `YC_SA_JSON_CREDENTIALS` (service account key JSON)
- `NOTIFY_API_KEY` (ключ для smoke-check запроса)

## 2) Последовательность deploy workflow

Файл: `.github/workflows/deploy.yml` (job привязан к GitHub Environment `production`).

1. Валидация обязательных переменных.
2. Проверка обязательных env и аутентификация через `YC_SA_JSON_CREDENTIALS`.
3. Деплой функции через `yc-actions/yc-sls-function@v4`.
4. Применение API Gateway и вычисление `NOTIFY_ENDPOINT` через `infra/scripts/yc_bootstrap_notify_endpoint.sh`.
   - Если задан `NOTIFY_PUBLIC_BASE_URL`, endpoint формируется как `<NOTIFY_PUBLIC_BASE_URL>/notify` и сохраняется в Lockbox/CI env вместо технического домена `*.apigw.yandexcloud.net`.
5. Smoke-check `POST /notify` через `infra/scripts/smoke_notify.sh`.


## 2.1) Bootstrap YC_API_GW_NAME и NOTIFY_ENDPOINT

Если gateway еще не создан или забыли значения переменных, можно восстановить автоматически:

```bash
YC_FOLDER_ID=<folder-id> \
YC_FUNCTION_ID=<function-id> \
YC_SERVICE_ACCOUNT_ID=<sa-id> \
LOCKBOX_SECRET_NAME=NG \
infra/scripts/yc_bootstrap_notify_endpoint.sh
```

Скрипт:
- создаст/обновит API Gateway `notify-gateway-gw` (или `YC_API_GW_NAME`, если передан);
- выведет готовые значения `YC_API_GW_NAME` и `NOTIFY_ENDPOINT`;
- при указании `LOCKBOX_SECRET_ID`/`LOCKBOX_SECRET_NAME` создаст новую версию секрета в Lockbox с этими ключами.


## 2.1) Bootstrap YC_API_GW_NAME и NOTIFY_ENDPOINT

Если gateway еще не создан или забыли значения переменных, можно восстановить автоматически:

```bash
YC_FOLDER_ID=<folder-id> \
YC_FUNCTION_ID=<function-id> \
YC_SERVICE_ACCOUNT_ID=<sa-id> \
LOCKBOX_SECRET_NAME=NG \
infra/scripts/yc_bootstrap_notify_endpoint.sh
```

Скрипт:
- создаст/обновит API Gateway `notify-gateway-gw` (или `YC_API_GW_NAME`, если передан);
- выведет готовые значения `YC_API_GW_NAME` и `NOTIFY_ENDPOINT`;
- при указании `LOCKBOX_SECRET_ID`/`LOCKBOX_SECRET_NAME` создаст новую версию секрета в Lockbox с этими ключами.


## 2.2) Публичный домен для API

Если API должен отвечать на вашем домене (например, `api.solofarm.ru`):

1. Настройте DNS-запись в зоне домена:
   - `api` -> `CNAME` на домен API Gateway (`<gateway-id>.apigw.yandexcloud.net`)
   - либо `A`/`CNAME` на внешний ingress/балансировщик, если используете его перед gateway.
2. Выпустите TLS-сертификат для `api.<ваш-домен>` (Yandex Certificate Manager или внешний сертификат).
3. Добавьте GitHub Variable/Secret `NOTIFY_PUBLIC_BASE_URL=https://api.<ваш-домен>`.
4. Запустите deploy workflow — smoke-check и Lockbox получат публичный endpoint.

## 3) Локальные проверки перед релизом

```bash
ruff check .
pytest -q

YC_FOLDER_ID=<folder-id> YC_FUNCTION_NAME=notify-gateway \
infra/scripts/yc_deploy_function.sh --dry-run

YC_FOLDER_ID=<folder-id> YC_API_GW_NAME=notify-gateway-gw YC_FUNCTION_ID=<function-id> YC_SERVICE_ACCOUNT_ID=<sa-id> \
infra/scripts/yc_apply_apigw.sh --dry-run

NOTIFY_ENDPOINT=https://example/notify NOTIFY_API_KEY=dummy \
infra/scripts/smoke_notify.sh --dry-run
```

## 4) Rollback (операционный)

### 4.1 Trigger rollback
Запускать rollback, если выполняется хотя бы один критерий:
- smoke-check падает 2 запуска подряд;
- рост 5xx на gateway > 5% в течение 5 минут;
- критический сбой отправки в Telegram (ошибки 502 из функции).

### 4.2 Function rollback
1. Получить список версий функции:
   ```bash
   yc serverless function version list --function-name "$YC_FUNCTION_NAME" --folder-id "$YC_FOLDER_ID"
   ```
2. Выбрать предыдущую стабильную версию (по времени/примечаниям релиза).
3. Обновить API Gateway spec, зафиксировав стабильный тег/версию интеграции.
4. Применить spec и выполнить smoke-check.

### 4.3 API Gateway rollback
1. Взять предыдущую стабильную спецификацию (`git checkout <stable-tag> -- infra/apigw.yaml`).
2. Рендерить и применить её:
   ```bash
   YC_FOLDER_ID=<folder-id> YC_API_GW_NAME=<gw-name> YC_FUNCTION_ID=<function-id> YC_SERVICE_ACCOUNT_ID=<sa-id> \
   infra/scripts/yc_apply_apigw.sh
   ```
3. Выполнить smoke-check и проверить логи.

### 4.4 Пост-rollback проверка
- `POST /notify` smoke-check возвращает `200` и `ok=true`.
- В логах функции нет всплеска 5xx в течение 10 минут.
- Операционный статус обновлён в `docs/execution/PROGRESS.md`.

## 5) Безопасность
- Никогда не печатать секреты (`YC_SA_JSON_CREDENTIALS`, `NOTIFY_API_KEY`, bot token).
- В shell-скриптах: `set -euo pipefail`.
- В секретных шагах CI: `set +x` и mask для секретов.
- `YC_API_GW_NAME`
- `YC_SERVICE_ACCOUNT_ID`
- `YC_FUNCTION_ID` (для рендера `infra/apigw.yaml`)

### GitHub Actions Secrets
- `YC_SA_JSON_CREDENTIALS` (service account key JSON)

> Значения секретов не должны выводиться в лог.

## 2) Workflow деплоя

Файл: `.github/workflows/deploy.yml` (job привязан к GitHub Environment `production`).

Триггеры:
- `push` в `main` (боевой деплой);
- `workflow_dispatch` (ручной запуск, поддержан `dry_run=true/false`).

Основные шаги:
1. Валидация обязательных переменных.
2. Проверка обязательных env и аутентификация через `YC_SA_JSON_CREDENTIALS`.
3. Деплой функции через `yc-actions/yc-sls-function@v4`.
4. Валидация/применение API Gateway через `infra/scripts/yc_bootstrap_notify_endpoint.sh`.

## 3) Локальный dry-run (без изменения ресурсов)

```bash
YC_FOLDER_ID=<folder-id> \
YC_FUNCTION_NAME=notify-gateway \
infra/scripts/yc_deploy_function.sh --dry-run

YC_FOLDER_ID=<folder-id> \
YC_API_GW_NAME=notify-gateway-gw \
YC_FUNCTION_ID=<function-id> \
YC_SERVICE_ACCOUNT_ID=<sa-id> \
infra/scripts/yc_apply_apigw.sh --dry-run
```

## 4) Rollback runbook

### 4.1 Function rollback
1. Найти предыдущую стабильную версию функции:
   ```bash
   yc serverless function version list --function-name "$YC_FUNCTION_NAME" --folder-id "$YC_FOLDER_ID"
   ```
2. Переключить integration/tag API Gateway на стабильную версию (или вернуть предыдущую спецификацию).
3. Выполнить smoke-check `POST /notify`.

### 4.2 API Gateway rollback
1. Хранить последнюю стабильную спецификацию (`infra/apigw.yaml` в main + release tag).
2. Применить предыдущую стабильную спецификацию:
   ```bash
   yc serverless api-gateway update --id "$YC_API_GW_ID" --spec <previous-spec-path>
   ```
3. Проверить ответ gateway endpoint и логи функции.

## 5) Безопасность и аудит
- Не печатать секреты (`YC_SA_JSON_CREDENTIALS`, bot token).
- Для shell-скриптов использовать `set -euo pipefail`.
- Для секретных участков принудительно держать `set +x`.
- Все ошибки деплоя фиксировать в `docs/execution/PROGRESS.md`.
