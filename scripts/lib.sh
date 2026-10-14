#!/usr/bin/env bash
# Shared helpers: load .env, validate it, resolve paths. Sourced by the other scripts.
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ENV_FILE="${ENV_FILE:-$REPO_ROOT/.env}"

die() { echo "ERROR: $*" >&2; exit 1; }
info() { echo "==> $*"; }

load_env() {
  [[ -f "$ENV_FILE" ]] || die "$ENV_FILE not found. Run: cp .env.example .env  and edit it."
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE"
  set +a

  local required=(RATHENA_DIR RATHENA_REF PACKETVER DB_HOST DB_PORT DB_NAME LOG_DB_NAME
                  DB_USER DB_PASS INTER_USER INTER_PASS SERVER_NAME PUBLIC_IP NEW_ACCOUNT)
  local v
  for v in "${required[@]}"; do
    [[ -n "${!v:-}" ]] || die "$v is empty in $ENV_FILE"
    [[ "${!v}" != CHANGE_ME* ]] || die "$v still has its placeholder value. Set a real value in $ENV_FILE"
  done

  [[ "$PACKETVER" =~ ^[0-9]{8}$ ]] || die "PACKETVER must be YYYYMMDD, got '$PACKETVER'"
  [[ "$NEW_ACCOUNT" =~ ^(yes|no)$ ]] || die "NEW_ACCOUNT must be yes or no"
  (( ${#SERVER_NAME} <= 20 )) || die "SERVER_NAME must be 20 characters or less"
  [[ ${#INTER_USER} -ge 4 && ${#INTER_PASS} -ge 4 ]] || die "INTER_USER and INTER_PASS need at least 4 characters"
  # Names are used inside SQL identifiers and config files: keep them simple.
  local n
  for n in DB_NAME LOG_DB_NAME DB_USER INTER_USER; do
    [[ "${!n}" =~ ^[A-Za-z0-9_]+$ ]] || die "$n may only contain letters, digits and _"
  done
  local p
  for p in DB_PASS INTER_PASS; do
    [[ "${!p}" != *"'"* && "${!p}" != *"\\"* && "${!p}" != *$'\n'* ]] \
      || die "$p must not contain quotes, backslashes or newlines"
  done

  case "$RATHENA_DIR" in
    /*) RATHENA_PATH="$RATHENA_DIR" ;;
    *)  RATHENA_PATH="$REPO_ROOT/$RATHENA_DIR" ;;
  esac
  export RATHENA_PATH
}

require_rathena() {
  [[ -f "$RATHENA_PATH/sql-files/main.sql" ]] \
    || die "rAthena not found at $RATHENA_PATH. Run scripts/install.sh first."
}

# Admin access to MariaDB. Default: socket auth as root (Ubuntu default).
# Override with e.g. MYSQL_ADMIN="mysql -uroot -p" if your root uses a password.
mysql_admin() {
  if [[ -n "${MYSQL_ADMIN:-}" ]]; then
    # shellcheck disable=SC2086
    $MYSQL_ADMIN "$@"
  elif [[ $EUID -eq 0 ]]; then
    mysql "$@"
  else
    sudo mysql "$@"
  fi
}
