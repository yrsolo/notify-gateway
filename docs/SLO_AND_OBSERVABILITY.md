# SLO-lite & operational checks (Stage 3)

## SLO-lite цели

- **Availability (gateway)**: не менее 99% ответов `2xx` на `POST /notify` за 24 часа.
- **Smoke success rate**: 100% успешных smoke-check после каждого deploy в `main`.
- **Delivery health proxy**: доля ответов функции `200 ok=true` не ниже 99% за rolling 1 час.

## Operational checks

### После каждого deploy
1. Smoke-check в workflow (`infra/scripts/smoke_notify.sh`).
2. Проверка логов функции за последние 10 минут на ошибки уровня `ERROR`.
3. Проверка HTTP-кодов gateway (нет всплеска `5xx`).

### Ежедневно
1. Просмотр тренда 5xx на gateway.
2. Проверка количества ошибок Telegram API в логах функции.
3. Подтверждение, что последний deploy имеет успешный smoke-check.

## Источники данных

- Логи Yandex Cloud Function (`yc serverless function logs read ...`).
- Логи/метрики API Gateway (response code distribution).
- Результаты GitHub Actions workflow `Deploy`.

## Триггеры эскалации

Эскалировать владельцу сервиса, если:
- smoke-check упал 2 раза подряд;
- доля `5xx` gateway > 5% в течение 5 минут;
- более 10 ошибок Telegram API за 10 минут;
- отсутствует успешный deploy + smoke-check в течение 24 часов.

## Команды быстрого triage

```bash
# Последние логи функции
yc serverless function logs read --name "$YC_FUNCTION_NAME" --folder-id "$YC_FOLDER_ID" --since 10m

# Dry-run smoke локально
NOTIFY_ENDPOINT=https://example/notify NOTIFY_API_KEY=dummy infra/scripts/smoke_notify.sh --dry-run
```
