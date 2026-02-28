# On-call & Ops playbook

## Escalation channels
- Primary: дежурный инженер (on-call rotation).
- Secondary: владелец сервиса notify-gateway.
- Platform escalation: DevOps/SRE команда.

## Response SLA
- P1 (полная недоступность `POST /notify`): ack до 10 минут, mitigation до 30 минут.
- P2 (частичная деградация, рост 5xx > 5%): ack до 20 минут, mitigation до 60 минут.
- P3 (локальные сбои, не влияющие на общий SLO): ack до 4 часов.

## Incident triage checklist
1. Проверить последний deploy workflow и smoke-check.
2. Проверить логи функции (`yc serverless function logs read ... --since 10m`).
3. Проверить ошибки gateway (4xx/5xx distribution).
4. Проверить статус Telegram API вызовов в логах.
5. Если требуется, выполнить rollback по `docs/DEPLOY_RUNBOOK.md`.

## Standard incident playbooks

### A) Smoke-check fails after deploy
1. Подтвердить, что проблема воспроизводится повторным smoke-check.
2. Выполнить rollback на последнюю стабильную версию.
3. Открыть incident запись и назначить owner на root-cause.

### B) Elevated 401/403
1. Проверить ротацию/валидность `NOTIFY_API_KEYS`.
2. Проверить, что клиенты используют актуальные ключи.
3. При подозрении на утечку — emergency rotation (`docs/SECRET_ROTATION.md`).

### C) Elevated 5xx / Telegram errors
1. Проверить валидность `TELEGRAM_BOT_TOKEN` и доступность Telegram API.
2. Проверить сетевые ошибки/timeout в логах функции.
3. При необходимости временно снизить нагрузку и выполнить rollback.

## Post-incident actions
- Добавить запись в `docs/execution/PROGRESS.md` (инцидент, действия, результат).
- Обновить playbook и SLO документ по итогам пост-мортема.
