#!/usr/bin/env bash
# Run the rAthena servers as the systemd service "rathena": they start by themselves
# after a reboot and are managed with: sudo systemctl start|stop|restart|status rathena
# Usage: scripts/install-service.sh   (run as the normal user that owns the repo; uses sudo)
# Safe to re-run: the unit file is rewritten and the service restarted.
# shellcheck source=scripts/lib.sh
source "$(dirname "$0")/lib.sh"
load_env
require_rathena

[[ $EUID -ne 0 ]] || die "Run this as the normal user that owns $RATHENA_PATH (not root or sudo); it calls sudo itself."
[[ "$RATHENA_PATH" != *[[:space:]]* ]] || die "systemd cannot use a rAthena path with spaces: $RATHENA_PATH"
for bin in athena-start login-server char-server map-server; do
  [[ -x "$RATHENA_PATH/$bin" ]] || die "$RATHENA_PATH/$bin is missing. Build rAthena first with scripts/install.sh."
done

db_unit=""
for unit in mariadb.service mysqld.service mysql.service; do
  if systemctl cat "$unit" >/dev/null 2>&1; then db_unit="$unit"; break; fi
done
[[ -n "$db_unit" ]] || info "No MariaDB/MySQL service found; rathena will not wait for the database at boot."

SERVICE_FILE=/etc/systemd/system/rathena.service
info "Writing $SERVICE_FILE (runs as $(id -un))"
sudo tee "$SERVICE_FILE" >/dev/null <<UNIT
[Unit]
Description=rAthena game servers ($SERVER_NAME)
Wants=network-online.target $db_unit
After=network-online.target $db_unit

[Service]
# athena-start launches login/char/map/web in the background and returns.
Type=oneshot
RemainAfterExit=yes
User=$(id -un)
WorkingDirectory=$RATHENA_PATH
ExecStart=$RATHENA_PATH/athena-start start --enlog
ExecStop=$RATHENA_PATH/athena-start stop
# Server output already goes to rathena/log/*.log; keep it out of the journal.
StandardOutput=null
TimeoutStopSec=120

[Install]
WantedBy=multi-user.target
UNIT

# Servers started by hand would block the service from starting its own copies.
info "Stopping servers that were started by hand (if any)"
(cd "$RATHENA_PATH" && ./athena-start stop) || true

sudo systemctl daemon-reload
sudo systemctl enable rathena.service
sudo systemctl restart rathena.service
sleep 3
(cd "$RATHENA_PATH" && ./athena-start status) || true
info "Done. The servers now start at boot. Map server needs ~20 seconds to load."
info "Manage them with: sudo systemctl restart rathena   (or stop / start / status)"
