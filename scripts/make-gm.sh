#!/usr/bin/env bash
# Set an account's group. Usage: scripts/make-gm.sh <userid> [group_id]
# group_id: 0 Player, 1 Super Player, 2 Support, 3 Script Manager, 4 Event Manager,
#           5 VIP, 10 Law Enforcement, 99 Admin (default). See rathena/conf/groups.yml.
# shellcheck source=scripts/lib.sh
source "$(dirname "$0")/lib.sh"
load_env

USERID="${1:-}"
GROUP="${2:-99}"
[[ "$USERID" =~ ^[A-Za-z0-9_]+$ ]] || die "Usage: $0 <userid> [group_id]  (userid without _M/_F)"
[[ "$GROUP" =~ ^(0|1|2|3|4|5|10|99)$ ]] || die "group_id must be one of 0 1 2 3 4 5 10 99"

rows="$(mysql_admin -N "$DB_NAME" -e \
  "UPDATE \`login\` SET group_id=$GROUP WHERE userid='$USERID' AND sex<>'S'; SELECT ROW_COUNT();")"
[[ "$rows" == "1" ]] || die "Account '$USERID' not found (or already in group $GROUP)"
info "$USERID is now group $GROUP. Relog the character to apply."
