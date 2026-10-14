#!/usr/bin/env bash
# Install the read-only website stats API on the game server (Amazon Linux 2023 or Ubuntu).
#   bash webapi/install.sh            install or update (safe to re-run; rotates the DB password)
#   bash webapi/install.sh --remove   stop it and remove the service, files and DB user
#
# What it sets up:
#   - MariaDB user 'webstats'@'localhost' with SELECT on only the columns the website shows
#   - system user 'sever-webapi', script in /opt/sever-webapi, DB login in /etc/sever-webapi/my.cnf
#   - systemd service 'sever-webapi' on TCP 8090 (starts on boot, ~15 MB RAM, capped at 64 MB)
# MariaDB itself stays private: never open 3306 in the security group.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${ENV_FILE:-$HERE/../.env}"
APP_DIR=/opt/sever-webapi
CONF_DIR=/etc/sever-webapi
SVC_USER=sever-webapi
UNIT=/etc/systemd/system/sever-webapi.service
PORT="${WEBAPI_PORT:-8090}"

die() { echo "ERROR: $*" >&2; exit 1; }
info() { echo "==> $*"; }
SUDO=""; [[ $EUID -eq 0 ]] || SUDO="sudo"
mysql_admin() { $SUDO mysql "$@"; }

if [[ "${1:-}" == "--remove" ]]; then
  info "Removing sever-webapi"
  $SUDO systemctl disable --now sever-webapi 2>/dev/null || true
  $SUDO rm -f "$UNIT"
  $SUDO systemctl daemon-reload
  $SUDO rm -rf "$APP_DIR" "$CONF_DIR"
  mysql_admin -e "DROP USER IF EXISTS 'webstats'@'localhost';"
  id "$SVC_USER" &>/dev/null && $SUDO userdel "$SVC_USER"
  info "Removed. You can now close TCP $PORT in the security group."
  exit 0
fi

command -v python3 >/dev/null || die "python3 not found"
command -v mysql >/dev/null || die "mysql client not found (MariaDB not installed?)"
command -v systemctl >/dev/null || die "systemd is required"
[[ -f "$ENV_FILE" ]] || die "$ENV_FILE not found (expected the game server .env)"

# Read only the two names we need from .env, without executing it.
env_value() { sed -n "s/^$1=//p" "$ENV_FILE" | tail -n1 | tr -d '"'"'"' \r'; }
DB_NAME="$(env_value DB_NAME)"; DB_NAME="${DB_NAME:-ragnarok}"
LOG_DB_NAME="$(env_value LOG_DB_NAME)"; LOG_DB_NAME="${LOG_DB_NAME:-ragnarok_log}"
for n in "$DB_NAME" "$LOG_DB_NAME"; do
  [[ "$n" =~ ^[A-Za-z0-9_]+$ ]] || die "database name '$n' may only contain letters, digits and _"
done
[[ "$PORT" =~ ^[0-9]+$ ]] || die "WEBAPI_PORT must be a number"

PASS="$(python3 -c 'import secrets; print(secrets.token_hex(24))')"

info "Creating read-only DB user 'webstats' (column-level SELECT only)"
mysql_admin <<SQL
CREATE USER IF NOT EXISTS 'webstats'@'localhost' IDENTIFIED BY '$PASS';
ALTER USER 'webstats'@'localhost' IDENTIFIED BY '$PASS';
GRANT SELECT (char_id, account_id, name, class, base_level, job_level, base_exp, online)
  ON \`$DB_NAME\`.\`char\` TO 'webstats'@'localhost';
GRANT SELECT (account_id, group_id) ON \`$DB_NAME\`.\`login\` TO 'webstats'@'localhost';
GRANT SELECT (guild_id, name, master) ON \`$DB_NAME\`.\`guild\` TO 'webstats'@'localhost';
GRANT SELECT (castle_id, guild_id) ON \`$DB_NAME\`.\`guild_castle\` TO 'webstats'@'localhost';
GRANT SELECT (kill_char_id) ON \`$LOG_DB_NAME\`.\`mvplog\` TO 'webstats'@'localhost';
FLUSH PRIVILEGES;
SQL

if ! id "$SVC_USER" &>/dev/null; then
  info "Creating system user $SVC_USER"
  $SUDO useradd --system --no-create-home --shell /sbin/nologin "$SVC_USER"
fi

info "Installing $APP_DIR/stats_api.py and $CONF_DIR/my.cnf"
$SUDO install -d -m 755 "$APP_DIR"
$SUDO install -m 644 "$HERE/stats_api.py" "$APP_DIR/stats_api.py"
$SUDO install -d -m 750 -o root -g "$SVC_USER" "$CONF_DIR"
printf '[client]\nuser=webstats\npassword=%s\n' "$PASS" \
  | $SUDO install -m 640 -o root -g "$SVC_USER" /dev/stdin "$CONF_DIR/my.cnf"

info "Writing systemd unit"
$SUDO tee "$UNIT" >/dev/null <<UNITEOF
[Unit]
Description=SEVER GAME Prontera website stats API (read-only)
After=network.target mariadb.service mysql.service

[Service]
User=$SVC_USER
Group=$SVC_USER
Environment=WEBAPI_MYSQL_CNF=$CONF_DIR/my.cnf WEBAPI_DB=$DB_NAME WEBAPI_LOG_DB=$LOG_DB_NAME WEBAPI_PORT=$PORT
ExecStart=/usr/bin/env python3 $APP_DIR/stats_api.py
Restart=on-failure
RestartSec=5
MemoryMax=64M
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=yes
PrivateTmp=yes
PrivateDevices=yes

[Install]
WantedBy=multi-user.target
UNITEOF

$SUDO systemctl daemon-reload
$SUDO systemctl enable sever-webapi >/dev/null
$SUDO systemctl restart sever-webapi

info "Checking http://127.0.0.1:$PORT/status"
for _ in 1 2 3 4 5; do
  if out="$(curl -fsS --max-time 5 "http://127.0.0.1:$PORT/status" 2>/dev/null)"; then
    echo "$out"
    echo
    info "Done. Last step: allow inbound TCP $PORT in the EC2 security group (keep 3306 closed)."
    exit 0
  fi
  sleep 1
done
$SUDO journalctl -u sever-webapi -n 20 --no-pager || true
die "the service did not answer on port $PORT (log above)"
