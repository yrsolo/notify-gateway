#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: yc_apply_apigw.sh [--dry-run]

Render and apply infra/apigw.yaml to Yandex API Gateway.

Required environment variables:
  YC_FOLDER_ID
  YC_API_GW_NAME
  YC_FUNCTION_ID
  YC_SERVICE_ACCOUNT_ID

Optional environment variables:
  APIGW_SPEC_TEMPLATE   (default: infra/apigw.yaml)
  APIGW_SPEC_RENDERED   (default: build/apigw.rendered.yaml)

Flags:
  --dry-run             Validate and render spec without yc apply
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
  for key in YC_FOLDER_ID YC_API_GW_NAME YC_FUNCTION_ID YC_SERVICE_ACCOUNT_ID; do
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

  if rg -q '<YOUR_' "${APIGW_SPEC_RENDERED}"; then
    echo "ERROR: rendered API Gateway spec still has unresolved placeholders" >&2
    exit 1
  fi
}

get_apigw_id_by_name() {
  yc serverless api-gateway list \
    --folder-id "${YC_FOLDER_ID}" \
    --format json | jq -r --arg name "${YC_API_GW_NAME}" '.[] | select(.name == $name) | .id' | head -n1
}

main() {
  local dry_run="false"
  APIGW_SPEC_TEMPLATE="${APIGW_SPEC_TEMPLATE:-infra/apigw.yaml}"
  APIGW_SPEC_RENDERED="${APIGW_SPEC_RENDERED:-build/apigw.rendered.yaml}"

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

  require_cmd sed
  require_cmd rg
  require_cmd jq
  validate_env

  if [[ ! -f "${APIGW_SPEC_TEMPLATE}" ]]; then
    echo "ERROR: API Gateway template not found: ${APIGW_SPEC_TEMPLATE}" >&2
    exit 1
  fi

  render_spec
  echo "Rendered API Gateway spec: ${APIGW_SPEC_RENDERED}"

  if [[ "${dry_run}" == "true" ]]; then
    echo "[dry-run] Skipping yc apply."
    echo "[dry-run] Planned steps:"
    echo "  1) Render ${APIGW_SPEC_TEMPLATE} with function/service-account IDs"
    echo "  2) Resolve API Gateway by name (${YC_API_GW_NAME})"
    echo "  3) Create gateway if absent, otherwise update existing gateway"
    exit 0
  fi

  require_cmd yc

  local api_gw_id
  api_gw_id=$(get_apigw_id_by_name)

  if [[ -z "${api_gw_id}" ]]; then
    echo "API Gateway does not exist, creating: ${YC_API_GW_NAME}"
    yc serverless api-gateway create \
      --name "${YC_API_GW_NAME}" \
      --folder-id "${YC_FOLDER_ID}" \
      --spec "${APIGW_SPEC_RENDERED}" >/dev/null
  else
    echo "Updating API Gateway: ${YC_API_GW_NAME} (${api_gw_id})"
    yc serverless api-gateway update \
      --id "${api_gw_id}" \
      --spec "${APIGW_SPEC_RENDERED}" >/dev/null
  fi

  echo "API Gateway apply completed: ${YC_API_GW_NAME}"
}

main "$@"
