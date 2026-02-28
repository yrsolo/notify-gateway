# Secret rotation policy

## Scope
Регламент покрывает секреты и чувствительные параметры для `notify-gateway`:
- `NOTIFY_API_KEYS`
- `TELEGRAM_BOT_TOKEN`
- `YC_TOKEN` / `YC_IAM_TOKEN` для CI (если используются)
- `NOTIFY_API_KEY` для smoke-check

## Periodicity
- `NOTIFY_API_KEYS`: каждые 30 дней или немедленно при подозрении на компрометацию.
- `TELEGRAM_BOT_TOKEN`: каждые 90 дней или немедленно при утечке.
- CI cloud tokens: по возможности только short-lived; если long-lived — ротация каждые 30 дней.
- Smoke-check API key: каждые 30 дней.

## Rotation workflow
1. Сгенерировать новый секрет в безопасном контуре (Lockbox / GitHub Secrets).
2. Обновить значение в хранилище секретов, не удаляя старое до верификации.
3. Выполнить `workflow_dispatch` с `dry_run=true`.
4. Выполнить боевой deploy (`dry_run=false`) и smoke-check.
5. Проверить логи функции и gateway (ошибки авторизации/Telegram).
6. Отключить/удалить старый секрет после успешной верификации.
7. Зафиксировать факт ротации в `docs/execution/PROGRESS.md`.

## Verification checklist after rotation
- [ ] Deploy workflow завершился успешно.
- [ ] Smoke-check `POST /notify` успешен (`200`, `ok=true`).
- [ ] Нет всплеска `401/403/5xx` в логах за 15 минут после ротации.
- [ ] Старое значение секрета деактивировано.
- [ ] Обновлена дата последней ротации в внутреннем трекере команды.

## Emergency rotation
Триггеры немедленной ротации:
- обнаружение секрета в логах/коммитах;
- несанкционированный доступ к CI/Cloud;
- аномальный рост `401` или подозрение на злоупотребление API key.

Шаги emergency-режима:
1. Немедленно отозвать компрометированный секрет.
2. Выпустить новый секрет и обновить окружение.
3. Выполнить deploy + smoke-check.
4. Провести пост-мортем и добавить preventive action в runbook.
