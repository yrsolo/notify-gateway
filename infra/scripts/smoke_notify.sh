#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: smoke_notify.sh [--dry-run] [--skip-send]

Smoke-check for POST /notify endpoint.

Required environment variables:
  NOTIFY_ENDPOINT       Full endpoint URL, e.g. https://<gateway>/notify
  NOTIFY_API_KEY        Bearer API key

Optional environment variables:
  SMOKE_PROJECT         (default: notify-gateway)
  SMOKE_ENV             (default: production)
  SMOKE_LEVEL           (default: info)
  SMOKE_TITLE           (default: smoke-check)
  SMOKE_MESSAGE         (default: smoke check from deploy workflow)
  SMOKE_EXPECT_STATUS   (default: 200)

Flags:
  --dry-run             Print request payload and exit without network call
  --skip-send           Alias for dry-run-like safe mode in pipelines
  -h, --help            Show help
USAGE
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "ERROR: required command '$1' is not installed" >&2
    exit 1
  fi
}

validate_env() {
  local missing=0

  if [[ -z "${NOTIFY_ENDPOINT:-}" ]]; then
    echo "ERROR: NOTIFY_ENDPOINT is required" >&2
    missing=1
  fi

  if [[ -z "${NOTIFY_API_KEY:-}" ]]; then
    echo "ERROR: NOTIFY_API_KEY is required" >&2
    missing=1
  fi

  if [[ "$missing" -ne 0 ]]; then
    exit 1
  fi
}

build_payload() {
  jq -n \
    --arg project "${SMOKE_PROJECT}" \
    --arg env "${SMOKE_ENV}" \
    --arg level "${SMOKE_LEVEL}" \
    --arg title "${SMOKE_TITLE}" \
    --arg message "${SMOKE_MESSAGE}" \
    '{project: $project, env: $env, level: $level, title: $title, message: $message, tags: ["smoke", "deploy"]}'
}

main() {
  local dry_run="false"
  local skip_send="false"

  SMOKE_PROJECT="${SMOKE_PROJECT:-notify-gateway}"
  SMOKE_ENV="${SMOKE_ENV:-production}"
  SMOKE_LEVEL="${SMOKE_LEVEL:-info}"
  SMOKE_TITLE="${SMOKE_TITLE:-smoke-check}"
  SMOKE_MESSAGE="${SMOKE_MESSAGE:-smoke check from deploy workflow}"
  SMOKE_EXPECT_STATUS="${SMOKE_EXPECT_STATUS:-200}"

  while (($#)); do
    case "$1" in
      --dry-run)
        dry_run="true"
        shift
        ;;
      --skip-send)
        skip_send="true"
        shift
        ;;
      -h|--help)
        usage
        exit 0
        ;;
      *)
        echo "ERROR: unknown argument: $1" >&2
        usage >&2
        exit 1
        ;;
    esac
  done

  require_cmd jq
  validate_env

  local payload
  payload=$(build_payload)

  echo "Smoke configuration:"
  echo "- endpoint: ${NOTIFY_ENDPOINT}"
  echo "- expected status: ${SMOKE_EXPECT_STATUS}"
  echo "- api key: [masked]"

  if [[ "${dry_run}" == "true" || "${skip_send}" == "true" ]]; then
    echo "[safe-mode] Skipping HTTP request."
    echo "[safe-mode] Payload preview: ${payload}"
    exit 0
  fi

  local tmp_body
  tmp_body=$(mktemp)

  local status
  status=$(curl -sS -o "${tmp_body}" -w "%{http_code}" \
    -X POST "${NOTIFY_ENDPOINT}" \
    -H "Authorization: Bearer ${NOTIFY_API_KEY}" \
    -H "Content-Type: application/json" \
    --data "${payload}")

  if [[ "${status}" != "${SMOKE_EXPECT_STATUS}" ]]; then
    echo "ERROR: unexpected status ${status}, expected ${SMOKE_EXPECT_STATUS}" >&2
    cat "${tmp_body}" >&2
    rm -f "${tmp_body}"
    exit 1
  fi

  if ! jq -e '.ok == true' "${tmp_body}" >/dev/null 2>&1; then
    echo "ERROR: response JSON does not contain ok=true" >&2
    cat "${tmp_body}" >&2
    rm -f "${tmp_body}"
    exit 1
  fi

  if ! jq -e '.telegram_message_id | numbers' "${tmp_body}" >/dev/null 2>&1; then
    echo "ERROR: response JSON does not contain numeric telegram_message_id" >&2
    cat "${tmp_body}" >&2
    rm -f "${tmp_body}"
    exit 1
  fi

  echo "Smoke-check passed with status ${status}."
  rm -f "${tmp_body}"
}

main "$@"
