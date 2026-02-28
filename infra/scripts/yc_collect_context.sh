#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: yc_collect_context.sh [--dry-run]

Collect Yandex Cloud context for deploy automation stage:
- validates required environment variables
- exchanges YC_TOKEN to IAM token if needed
- collects folder-related resources (functions, api gateways, service accounts)

Environment:
  Required:
    YC_FOLDER_ID            Target folder id
    YC_TOKEN or YC_IAM_TOKEN
  Optional:
    YC_CLOUD_ID             Cloud id for reference
    YC_FUNCTION_NAME        Function name hint for filtering
    YC_API_GW_NAME          API Gateway name hint for filtering

Flags:
  --dry-run                 Validate setup and print planned calls without making API requests
  -h, --help                Show this help
USAGE
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "ERROR: required command '$1' is not installed" >&2
    exit 1
  fi
}

mask_value() {
  local value="$1"
  local keep="${2:-6}"
  if [[ -z "$value" ]]; then
    echo "<empty>"
    return
  fi
  if ((${#value} <= keep)); then
    echo "***"
    return
  fi
  printf '%s***' "${value:0:keep}"
}

validate_env() {
  local missing=0

  if [[ -z "${YC_FOLDER_ID:-}" ]]; then
    echo "ERROR: YC_FOLDER_ID is required" >&2
    missing=1
  fi

  if [[ -z "${YC_TOKEN:-}" && -z "${YC_IAM_TOKEN:-}" ]]; then
    echo "ERROR: either YC_TOKEN or YC_IAM_TOKEN must be set" >&2
    missing=1
  fi

  if [[ "$missing" -ne 0 ]]; then
    exit 1
  fi
}

get_iam_token() {
  if [[ -n "${YC_IAM_TOKEN:-}" ]]; then
    printf '%s' "$YC_IAM_TOKEN"
    return
  fi

  local iam_json
  iam_json=$(curl -sS -X POST "https://iam.api.cloud.yandex.net/iam/v1/tokens" \
    -H "Content-Type: application/json" \
    -d "{\"yandexPassportOauthToken\":\"${YC_TOKEN}\"}")

  local iam_token
  iam_token=$(jq -r '.iamToken // empty' <<<"$iam_json")
  if [[ -z "$iam_token" ]]; then
    echo "ERROR: failed to exchange YC_TOKEN to IAM token" >&2
    jq . <<<"$iam_json" >&2 || true
    exit 1
  fi

  printf '%s' "$iam_token"
}

api_get() {
  local token="$1"
  local url="$2"
  curl -sS -H "Authorization: Bearer ${token}" "$url"
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

  require_cmd curl
  require_cmd jq
  validate_env

  echo "Collecting YC context"
  echo "- YC_FOLDER_ID: ${YC_FOLDER_ID}"
  echo "- YC_CLOUD_ID: ${YC_CLOUD_ID:-<not-set>}"
  echo "- YC_FUNCTION_NAME hint: ${YC_FUNCTION_NAME:-<not-set>}"
  echo "- YC_API_GW_NAME hint: ${YC_API_GW_NAME:-<not-set>}"

  if [[ "$dry_run" == "true" ]]; then
    echo "[dry-run] Skipping IAM exchange and API calls."
    echo "[dry-run] Would call:"
    echo "  1) POST https://iam.api.cloud.yandex.net/iam/v1/tokens (if YC_IAM_TOKEN is absent)"
    echo "  2) GET  https://resource-manager.api.cloud.yandex.net/resource-manager/v1/folders/${YC_FOLDER_ID}"
    echo "  3) GET  https://serverless-functions.api.cloud.yandex.net/functions/v1/functions?folderId=${YC_FOLDER_ID}"
    echo "  4) GET  https://serverless-apigateway.api.cloud.yandex.net/apigateways/v1/apigateways?folderId=${YC_FOLDER_ID}"
    echo "  5) GET  https://iam.api.cloud.yandex.net/iam/v1/serviceAccounts?folderId=${YC_FOLDER_ID}"
    exit 0
  fi

  local iam_token
  iam_token=$(get_iam_token)
  echo "- IAM token: $(mask_value "$iam_token" 8)"

  local folder_json functions_json apigw_json sa_json
  folder_json=$(api_get "$iam_token" "https://resource-manager.api.cloud.yandex.net/resource-manager/v1/folders/${YC_FOLDER_ID}")
  functions_json=$(api_get "$iam_token" "https://serverless-functions.api.cloud.yandex.net/functions/v1/functions?folderId=${YC_FOLDER_ID}")
  apigw_json=$(api_get "$iam_token" "https://serverless-apigateway.api.cloud.yandex.net/apigateways/v1/apigateways?folderId=${YC_FOLDER_ID}")
  sa_json=$(api_get "$iam_token" "https://iam.api.cloud.yandex.net/iam/v1/serviceAccounts?folderId=${YC_FOLDER_ID}")

  echo
  echo "Folder:"
  jq '{id, name, cloudId, status}' <<<"$folder_json"

  echo
  echo "Functions:"
  jq -r '.functions[]? | "- \(.id)\t\(.name)\truntime=\(.runtime // "-")"' <<<"$functions_json"

  echo
  echo "API Gateways:"
  jq -r '.apiGateways[]? | "- \(.id)\t\(.name)"' <<<"$apigw_json"

  echo
  echo "Service Accounts:"
  jq -r '.serviceAccounts[]? | "- \(.id)\t\(.name)"' <<<"$sa_json"
}

main "$@"
