#!/usr/bin/env bash
# Install build dependencies + MariaDB, clone rAthena and compile it (Ubuntu/Debian).
# Usage: scripts/install-ubuntu.sh [--skip-apt]
# shellcheck source=scripts/lib.sh
source "$(dirname "$0")/lib.sh"
load_env

if [[ "${1:-}" != "--skip-apt" ]]; then
  info "Installing packages (sudo)"
  SUDO=""; [[ $EUID -eq 0 ]] || SUDO="sudo"
  $SUDO apt-get update
  $SUDO apt-get install -y git make gcc g++ zlib1g-dev libpcre3-dev \
    libmariadb-dev libmariadb-dev-compat mariadb-server
fi

if [[ -d "$RATHENA_PATH/.git" ]]; then
  info "Updating rAthena in $RATHENA_PATH ($RATHENA_REF)"
  git -C "$RATHENA_PATH" fetch --depth 1 origin "$RATHENA_REF"
  git -C "$RATHENA_PATH" checkout --detach FETCH_HEAD
else
  info "Cloning rAthena ($RATHENA_REF) into $RATHENA_PATH"
  git clone --depth 1 --branch "$RATHENA_REF" https://github.com/rathena/rathena.git "$RATHENA_PATH"
fi

info "Compiling with PACKETVER=$PACKETVER (this takes a few minutes)"
cd "$RATHENA_PATH" || die "cannot cd to $RATHENA_PATH"
./configure --enable-packetver="$PACKETVER"
make clean
make server -j"$(nproc)"

for bin in login-server char-server map-server; do
  [[ -x "$RATHENA_PATH/$bin" ]] || die "Build finished but $bin is missing"
done
info "Build OK. Next: scripts/setup-db.sh"
