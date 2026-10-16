#!/usr/bin/env bash
# Add a swap file so rAthena can compile on small (1 GB RAM) servers.
# Usage: scripts/add-swap.sh [size_in_GB]   (default 2)
set -euo pipefail
SIZE_GB="${1:-2}"
[[ "$SIZE_GB" =~ ^[1-8]$ ]] || { echo "ERROR: size must be 1-8 (GB)" >&2; exit 1; }
SUDO=""; [[ $EUID -eq 0 ]] || SUDO="sudo"

if [[ -f /swapfile ]] || [[ "$(awk '/SwapTotal/ {print $2}' /proc/meminfo)" != "0" ]]; then
  echo "==> Swap already present:"; free -h; exit 0
fi
echo "==> Creating ${SIZE_GB}G swap file at /swapfile"
$SUDO dd if=/dev/zero of=/swapfile bs=1M count=$((SIZE_GB * 1024)) status=progress
$SUDO chmod 600 /swapfile
$SUDO mkswap /swapfile
$SUDO swapon /swapfile
grep -q '^/swapfile ' /etc/fstab || echo '/swapfile none swap sw 0 0' | $SUDO tee -a /etc/fstab >/dev/null
free -h
