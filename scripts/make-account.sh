#!/usr/bin/env bash
# Create a game account, or reset its password if it already exists. The password is typed here,
# hidden, and never leaves this machine. Set MAKE_ACCOUNT_PASS to skip the prompt for a one-line run.
# Works even when NEW_ACCOUNT=no (no _M signup needed).
# Usage: scripts/make-account.sh <userid> [M|F]   (userid without _M/_F; sex only matters for a new account)
# Passwords are stored in plain text unless use_MD5_passwords is turned on in login_athena.conf.
# shellcheck source=scripts/lib.sh
source "$(dirname "$0")/lib.sh"
load_env

USERID="${1:-}"
SEX="${2:-M}"
[[ "$USERID" =~ ^[A-Za-z0-9_]+$ ]] || die "Usage: $0 <userid> [M|F]  (userid without _M/_F)"
(( ${#USERID} >= 4 && ${#USERID} <= 23 )) || die "The userid needs 4 to 23 characters."
[[ "$SEX" =~ ^[MF]$ ]] || die "Sex must be M or F"

# MAKE_ACCOUNT_PASS=... skips the prompt (the password then stays in this shell's history).
if [[ -n "${MAKE_ACCOUNT_PASS:-}" ]]; then
  PASS1="$MAKE_ACCOUNT_PASS"; PASS2="$MAKE_ACCOUNT_PASS"
else
  read -r -s -p "Password for $USERID (6-23 characters, typing is hidden): " PASS1; echo
  read -r -s -p "Type it again: " PASS2; echo
fi
[[ "$PASS1" == "$PASS2" ]] || die "The two passwords are different. Nothing was changed."
(( ${#PASS1} >= 6 && ${#PASS1} <= 23 )) || die "The password needs 6 to 23 characters. Nothing was changed."
[[ "$PASS1" =~ ^[A-Za-z0-9._@#%+=-]+$ ]] \
  || die "Use only letters, digits and . _ @ # % + = - . Nothing was changed."

kind="$(mysql_admin -N "$DB_NAME" -e \
  "SELECT IF(COUNT(*)=0,'new',IF(SUM(sex='S')>0,'server','old')) FROM \`login\` WHERE userid='$USERID';")"
case "$kind" in
  server) die "'$USERID' is the internal server account. Pick another userid." ;;
  new)
    mysql_admin "$DB_NAME" -e \
      "INSERT INTO \`login\` (userid, user_pass, sex, email) VALUES ('$USERID','$PASS1','$SEX','a@a.com');"
    info "Account $USERID created. Log in with $USERID (no _M) and the password you typed." ;;
  old)
    mysql_admin "$DB_NAME" -e "UPDATE \`login\` SET user_pass='$PASS1' WHERE userid='$USERID' AND sex<>'S';"
    info "Password of $USERID updated. Log in with $USERID (no _M) and the new password." ;;
  *) die "Could not read the account table (got '$kind'). Is the database running?" ;;
esac
