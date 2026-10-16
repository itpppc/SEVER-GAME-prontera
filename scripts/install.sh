#!/usr/bin/env bash
# Install build dependencies + MariaDB, clone rAthena and compile it.
# Supports Ubuntu/Debian (apt) and Amazon Linux 2023 / RHEL / Fedora (dnf).
# Usage: scripts/install.sh [--skip-packages]
# shellcheck source=scripts/lib.sh
source "$(dirname "$0")/lib.sh"
load_env

SUDO=""; [[ $EUID -eq 0 ]] || SUDO="sudo"

install_packages() {
  if command -v apt-get >/dev/null; then
    info "Installing packages with apt (sudo)"
    $SUDO apt-get update
    $SUDO apt-get install -y git make gcc g++ zlib1g-dev libpcre3-dev \
      libmariadb-dev libmariadb-dev-compat mariadb-server
  elif command -v dnf >/dev/null; then
    info "Installing packages with dnf (sudo)"
    $SUDO dnf install -y git make gcc gcc-c++ zlib-devel
    # PCRE is optional for rAthena; ignore if the package is unavailable
    $SUDO dnf install -y pcre-devel || info "pcre-devel not available, building without PCRE"
    # MariaDB server + client library (Amazon Linux 2023 ships mariadb105)
    $SUDO dnf install -y mariadb105-server || $SUDO dnf install -y mariadb-server
    $SUDO dnf install -y mariadb-connector-c-devel || $SUDO dnf install -y mariadb105-devel
    $SUDO systemctl enable --now mariadb
  else
    die "Unsupported OS: need apt-get or dnf"
  fi
}

[[ "${1:-}" == "--skip-packages" || "${1:-}" == "--skip-apt" ]] || install_packages

if [[ -d "$RATHENA_PATH/.git" ]]; then
  info "Updating rAthena in $RATHENA_PATH ($RATHENA_REF)"
  git -C "$RATHENA_PATH" fetch --depth 1 origin "$RATHENA_REF"
  git -C "$RATHENA_PATH" checkout --detach FETCH_HEAD
else
  info "Cloning rAthena ($RATHENA_REF) into $RATHENA_PATH"
  git clone --depth 1 --branch "$RATHENA_REF" https://github.com/rathena/rathena.git "$RATHENA_PATH"
fi

configure_args=(--enable-packetver="$PACKETVER")
# Some distros only ship mariadb_config (no mysql_config)
if ! command -v mysql_config >/dev/null && command -v mariadb_config >/dev/null; then
  configure_args+=(--with-mysql="$(command -v mariadb_config)")
fi

# Limit parallel jobs on small machines so the compiler is not killed for lack of memory
mem_mb=$(awk '/MemTotal/ {print int($2/1024)}' /proc/meminfo)
swap_mb=$(awk '/SwapTotal/ {print int($2/1024)}' /proc/meminfo)
jobs=$(nproc)
if (( mem_mb + swap_mb < 3000 )); then
  jobs=1
  (( swap_mb > 0 )) || info "WARNING: low memory and no swap. Run scripts/add-swap.sh first if the build gets killed."
fi

info "Compiling with PACKETVER=$PACKETVER using $jobs job(s) (this takes a while)"
cd "$RATHENA_PATH" || die "cannot cd to $RATHENA_PATH"
./configure "${configure_args[@]}"
make clean
make server -j"$jobs"

for bin in login-server char-server map-server; do
  [[ -x "$RATHENA_PATH/$bin" ]] || die "Build finished but $bin is missing"
done
info "Build OK. Next: scripts/setup-db.sh"
