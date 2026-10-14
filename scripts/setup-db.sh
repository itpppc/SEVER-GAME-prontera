#!/usr/bin/env bash
# Create the databases + DB user, import rAthena SQL, and set the inter-server account.
# Safe to re-run: existing tables are left alone, credentials are updated.
# shellcheck source=scripts/lib.sh
source "$(dirname "$0")/lib.sh"
load_env
require_rathena

SQL="$RATHENA_PATH/sql-files"

info "Creating databases '$DB_NAME', '$LOG_DB_NAME' and user '$DB_USER'"
mysql_admin <<SQLEOF
CREATE DATABASE IF NOT EXISTS \`$DB_NAME\` CHARACTER SET utf8mb4;
CREATE DATABASE IF NOT EXISTS \`$LOG_DB_NAME\` CHARACTER SET utf8mb4;
CREATE USER IF NOT EXISTS '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASS';
CREATE USER IF NOT EXISTS '$DB_USER'@'127.0.0.1' IDENTIFIED BY '$DB_PASS';
ALTER USER '$DB_USER'@'localhost' IDENTIFIED BY '$DB_PASS';
ALTER USER '$DB_USER'@'127.0.0.1' IDENTIFIED BY '$DB_PASS';
GRANT ALL PRIVILEGES ON \`$DB_NAME\`.* TO '$DB_USER'@'localhost', '$DB_USER'@'127.0.0.1';
GRANT ALL PRIVILEGES ON \`$LOG_DB_NAME\`.* TO '$DB_USER'@'localhost', '$DB_USER'@'127.0.0.1';
FLUSH PRIVILEGES;
SQLEOF

table_exists() { # db table
  [[ -n "$(mysql_admin -N -e "SHOW TABLES FROM \`$1\` LIKE '$2'")" ]]
}

if table_exists "$DB_NAME" login; then
  info "Main schema already imported, skipping"
else
  info "Importing main.sql, web.sql, roulette_default_data.sql into $DB_NAME"
  for f in main.sql web.sql roulette_default_data.sql; do
    mysql_admin "$DB_NAME" < "$SQL/$f"
  done
fi

if table_exists "$LOG_DB_NAME" picklog; then
  info "Log schema already imported, skipping"
else
  info "Importing logs.sql into $LOG_DB_NAME"
  mysql_admin "$LOG_DB_NAME" < "$SQL/logs.sql"
fi

info "Setting inter-server account (account_id 1, replaces default s1/p1)"
mysql_admin "$DB_NAME" -e \
  "UPDATE \`login\` SET userid='$INTER_USER', user_pass='$INTER_PASS' WHERE account_id=1 AND sex='S';"

info "Database ready. Next: scripts/apply-config.sh"
