#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: yc_deploy_function.sh [--dry-run] [--entrypoint ENTRYPOINT] [--runtime RUNTIME]

Deploy notify-gateway function to Yandex Cloud using yc CLI.
Script supports create/update by function name and does not print secret values.

Required environment variables:
  YC_FOLDER_ID
  YC_FUNCTION_NAME

Optional environment variables:
  FUNCTION_SOURCE_DIR        (default: src)
  FUNCTION_ZIP_PATH          (default: build/function.zip)
  FUNCTION_RUNTIME           (default: python311)
  FUNCTION_ENTRYPOINT        (default: handler.handler)
  FUNCTION_MEMORY_MB         (default: 128)
  FUNCTION_TIMEOUT_SEC       (default: 10)
  FUNCTION_SERVICE_ACCOUNT_ID
  FUNCTION_ENV_FILE          (path to non-secret env vars)
  FUNCTION_SECRETS_FILE      (path to secret refs for yc --secret)

Flags:
  --dry-run                  Print planned actions without executing yc calls
  --entrypoint VALUE         Override entrypoint
  --runtime VALUE            Override runtime
  -h, --help                 Show help
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

  if [[ -z "${YC_FOLDER_ID:-}" ]]; then
    echo "ERROR: YC_FOLDER_ID is required" >&2
    missing=1
  fi

  if [[ -z "${YC_FUNCTION_NAME:-}" ]]; then
    echo "ERROR: YC_FUNCTION_NAME is required" >&2
    missing=1
  fi

  if [[ "$missing" -ne 0 ]]; then
    exit 1
  fi
}

print_masked_summary() {
  echo "Deploy configuration:"
  echo "- folder: ${YC_FOLDER_ID}"
  echo "- function: ${YC_FUNCTION_NAME}"
  echo "- source dir: ${FUNCTION_SOURCE_DIR}"
  echo "- artifact: ${FUNCTION_ZIP_PATH}"
  echo "- runtime: ${FUNCTION_RUNTIME}"
  echo "- entrypoint: ${FUNCTION_ENTRYPOINT}"
  echo "- memory: ${FUNCTION_MEMORY_MB} MB"
  echo "- timeout: ${FUNCTION_TIMEOUT_SEC} sec"
  echo "- service account id: ${FUNCTION_SERVICE_ACCOUNT_ID:-<not-set>}"
  echo "- env file: ${FUNCTION_ENV_FILE:-<not-set>}"
  echo "- secrets file: ${FUNCTION_SECRETS_FILE:-<not-set>}"
}

prepare_artifact() {
  mkdir -p "$(dirname "${FUNCTION_ZIP_PATH}")"
  rm -f "${FUNCTION_ZIP_PATH}"
  (
    cd "${FUNCTION_SOURCE_DIR}"
    zip -qr "../${FUNCTION_ZIP_PATH}" .
  )
}

function_exists() {
  local found
  found=$(yc serverless function list \
    --folder-id "${YC_FOLDER_ID}" \
    --format json | jq -r --arg name "${YC_FUNCTION_NAME}" '.[] | select(.name == $name) | .id' | head -n1)

  [[ -n "${found}" ]]
}

build_version_args() {
  local args=()

  args+=(--runtime "${FUNCTION_RUNTIME}")
  args+=(--entrypoint "${FUNCTION_ENTRYPOINT}")
  args+=(--memory "${FUNCTION_MEMORY_MB}m")
  args+=(--execution-timeout "${FUNCTION_TIMEOUT_SEC}s")
  args+=(--source-path "${FUNCTION_ZIP_PATH}")

  if [[ -n "${FUNCTION_SERVICE_ACCOUNT_ID:-}" ]]; then
    args+=(--service-account-id "${FUNCTION_SERVICE_ACCOUNT_ID}")
  fi

  if [[ -n "${FUNCTION_ENV_FILE:-}" ]]; then
    args+=(--environment-file "${FUNCTION_ENV_FILE}")
  fi

  if [[ -n "${FUNCTION_SECRETS_FILE:-}" ]]; then
    while IFS= read -r secret_line; do
      [[ -z "${secret_line}" ]] && continue
      [[ "${secret_line}" =~ ^# ]] && continue
      args+=(--secret "${secret_line}")
    done < "${FUNCTION_SECRETS_FILE}"
  fi

  printf '%s\n' "${args[@]}"
}

main() {
  local dry_run="false"

  FUNCTION_SOURCE_DIR="${FUNCTION_SOURCE_DIR:-src}"
  FUNCTION_ZIP_PATH="${FUNCTION_ZIP_PATH:-build/function.zip}"
  FUNCTION_RUNTIME="${FUNCTION_RUNTIME:-python311}"
  FUNCTION_ENTRYPOINT="${FUNCTION_ENTRYPOINT:-handler.handler}"
  FUNCTION_MEMORY_MB="${FUNCTION_MEMORY_MB:-128}"
  FUNCTION_TIMEOUT_SEC="${FUNCTION_TIMEOUT_SEC:-10}"

  while (($#)); do
    case "$1" in
      --dry-run)
        dry_run="true"
        shift
        ;;
      --entrypoint)
        FUNCTION_ENTRYPOINT="$2"
        shift 2
        ;;
      --runtime)
        FUNCTION_RUNTIME="$2"
        shift 2
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

  require_cmd zip
  require_cmd jq
  validate_env

  if [[ ! -d "${FUNCTION_SOURCE_DIR}" ]]; then
    echo "ERROR: source directory does not exist: ${FUNCTION_SOURCE_DIR}" >&2
    exit 1
  fi

  if [[ -n "${FUNCTION_ENV_FILE:-}" && ! -f "${FUNCTION_ENV_FILE}" ]]; then
    echo "ERROR: FUNCTION_ENV_FILE not found: ${FUNCTION_ENV_FILE}" >&2
    exit 1
  fi

  if [[ -n "${FUNCTION_SECRETS_FILE:-}" && ! -f "${FUNCTION_SECRETS_FILE}" ]]; then
    echo "ERROR: FUNCTION_SECRETS_FILE not found: ${FUNCTION_SECRETS_FILE}" >&2
    exit 1
  fi

  print_masked_summary

  if [[ "${dry_run}" == "true" ]]; then
    echo "[dry-run] Skipping artifact build and yc API calls."
    echo "[dry-run] Planned steps:"
    echo "  1) Build zip artifact from ${FUNCTION_SOURCE_DIR} -> ${FUNCTION_ZIP_PATH}"
    echo "  2) Check function existence by name in folder ${YC_FOLDER_ID}"
    echo "  3) Create function if absent"
    echo "  4) Create new function version with runtime, entrypoint, resources and secret refs"
    exit 0
  fi

  require_cmd yc

  prepare_artifact

  if function_exists; then
    echo "Function exists: ${YC_FUNCTION_NAME}"
  else
    echo "Function does not exist, creating: ${YC_FUNCTION_NAME}"
    yc serverless function create --name "${YC_FUNCTION_NAME}" --folder-id "${YC_FOLDER_ID}" >/dev/null
  fi

  mapfile -t version_args < <(build_version_args)

  yc serverless function version create \
    --function-name "${YC_FUNCTION_NAME}" \
    --folder-id "${YC_FOLDER_ID}" \
    "${version_args[@]}"

  echo "Deploy completed for function: ${YC_FUNCTION_NAME}"
}

main "$@"
