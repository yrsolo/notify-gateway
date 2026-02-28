#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: yc_bootstrap_notify_endpoint.sh [--dry-run]

Creates or updates API Gateway for /notify and prints values for:
  - YC_API_GW_NAME
  - NOTIFY_ENDPOINT

Required environment variables:
  YC_FOLDER_ID
  YC_FUNCTION_ID
  YC_SERVICE_ACCOUNT_ID

Optional environment variables:
  YC_API_GW_NAME      (default: notify-gateway-gw)
  APIGW_SPEC_TEMPLATE (default: infra/apigw.yaml)
  APIGW_SPEC_RENDERED (default: build/apigw.rendered.yaml)
  NOTIFY_PUBLIC_BASE_URL Public API base URL (e.g. https://api.example.com)
  LOCKBOX_SECRET_ID   Lockbox secret id for syncing variables
  LOCKBOX_SECRET_NAME Lockbox secret name (used if id is not provided)

Flags:
  --dry-run           Render and print values without changing cloud resources
  -h, --help          Show help
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
  for key in YC_FOLDER_ID YC_FUNCTION_ID YC_SERVICE_ACCOUNT_ID; do
    if [[ -z "${!key:-}" ]]; then
      echo "ERROR: ${key} is required" >&2
      missing=1
    fi
  done

  if [[ "$missing" -ne 0 ]]; then
    exit 1
  fi
}

render_spec() {
  mkdir -p "$(dirname "${APIGW_SPEC_RENDERED}")"
  sed \
    -e "s|<YOUR_FUNCTION_ID>|${YC_FUNCTION_ID}|g" \
    -e "s|<YOUR_SERVICE_ACCOUNT_ID>|${YC_SERVICE_ACCOUNT_ID}|g" \
    "${APIGW_SPEC_TEMPLATE}" > "${APIGW_SPEC_RENDERED}"

  if grep -q '<YOUR_' "${APIGW_SPEC_RENDERED}"; then
    echo "ERROR: rendered API Gateway spec still has unresolved placeholders" >&2
    exit 1
  fi
}

resolve_gateway() {
  yc serverless api-gateway list --folder-id "${YC_FOLDER_ID}" --format json \
    | jq -r --arg name "${YC_API_GW_NAME}" '.[] | select(.name == $name) | .id' \
    | head -n1
}

apply_gateway() {
  local gw_id
  gw_id=$(resolve_gateway)

  if [[ -z "$gw_id" ]]; then
    yc serverless api-gateway create \
      --name "${YC_API_GW_NAME}" \
      --folder-id "${YC_FOLDER_ID}" \
      --spec "${APIGW_SPEC_RENDERED}" >/dev/null
  else
    yc serverless api-gateway update \
      --id "$gw_id" \
      --spec "${APIGW_SPEC_RENDERED}" >/dev/null
  fi
}

resolve_endpoint() {
  if [[ -n "${NOTIFY_PUBLIC_BASE_URL:-}" ]]; then
    local base_url
    base_url="${NOTIFY_PUBLIC_BASE_URL%/}"
    printf '%s/notify' "$base_url"
    return 0
  fi

  local domain
  domain=$(yc serverless api-gateway list --folder-id "${YC_FOLDER_ID}" --format json \
    | jq -r --arg name "${YC_API_GW_NAME}" '.[] | select(.name == $name) | .domain' \
    | head -n1)

  if [[ -z "$domain" || "$domain" == "null" ]]; then
    echo "ERROR: failed to resolve domain for API Gateway '${YC_API_GW_NAME}'" >&2
    exit 1
  fi

  printf 'https://%s/notify' "$domain"
}

sync_lockbox() {
  local endpoint="$1"
  local target_flag=""
  local target_value=""

  if [[ -n "${LOCKBOX_SECRET_ID:-}" ]]; then
    target_flag="--id"
    target_value="${LOCKBOX_SECRET_ID}"
  elif [[ -n "${LOCKBOX_SECRET_NAME:-}" ]]; then
    target_flag="--name"
    target_value="${LOCKBOX_SECRET_NAME}"
  else
    return 0
  fi

  local payload
  payload=$(jq -cn \
    --arg gw "${YC_API_GW_NAME}" \
    --arg endpoint "$endpoint" \
    '[
      {"key":"YC_API_GW_NAME","text_value":$gw},
      {"key":"NOTIFY_ENDPOINT","text_value":$endpoint}
    ]')

  yc lockbox secret add-version "$target_flag" "$target_value" --payload "$payload" >/dev/null
  echo "Lockbox secret updated: ${target_value}"
}

main() {
  local dry_run="false"

  while (($#)); do
    case "$1" in
      --dry-run)
        dry_run="true"
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

  APIGW_SPEC_TEMPLATE="${APIGW_SPEC_TEMPLATE:-infra/apigw.yaml}"
  APIGW_SPEC_RENDERED="${APIGW_SPEC_RENDERED:-build/apigw.rendered.yaml}"
  YC_API_GW_NAME="${YC_API_GW_NAME:-notify-gateway-gw}"

  if [[ "$dry_run" == "false" || -z "${NOTIFY_PUBLIC_BASE_URL:-}" ]]; then
    require_cmd yc
  fi

  require_cmd jq
  require_cmd sed

  validate_env
  render_spec

  if [[ "$dry_run" == "false" ]]; then
    apply_gateway
  fi

  local endpoint
  endpoint=$(resolve_endpoint)

  echo "YC_API_GW_NAME=${YC_API_GW_NAME}"
  echo "NOTIFY_ENDPOINT=${endpoint}"

  if [[ "$dry_run" == "false" ]]; then
    sync_lockbox "$endpoint"
  fi
}

main "$@"
