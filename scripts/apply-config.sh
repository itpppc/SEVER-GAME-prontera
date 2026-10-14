#!/usr/bin/env bash
# Render config/import/* with values from .env into rathena/conf/import/.
# shellcheck source=scripts/lib.sh
source "$(dirname "$0")/lib.sh"
load_env
require_rathena

SRC="$REPO_ROOT/config/import"
DST="$RATHENA_PATH/conf/import"
mkdir -p "$DST"

render() { # src dst
  local content key
  content="$(<"$1")"
  for key in DB_HOST DB_PORT DB_NAME LOG_DB_NAME DB_USER DB_PASS INTER_USER INTER_PASS \
             SERVER_NAME PUBLIC_IP NEW_ACCOUNT; do
    content="${content//\{\{$key\}\}/${!key}}"
  done
  local placeholder='\{\{[A-Z_]+\}\}'
  [[ ! "$content" =~ $placeholder ]] || die "Unfilled placeholder ${BASH_REMATCH[0]} in $1"
  printf '%s\n' "$content" > "$2"
  chmod 600 "$2"
}

for f in "$SRC"/*; do
  name="$(basename "$f")"
  render "$f" "$DST/$name"
  info "Wrote conf/import/$name"
done
info "Config applied. Start the server: cd $RATHENA_PATH && ./athena-start start --enlog"
