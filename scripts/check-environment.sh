#!/usr/bin/env bash
set -euo pipefail

missing=0

check() {
  local command_name="$1"
  local purpose="$2"
  if command -v "${command_name}" >/dev/null 2>&1; then
    printf '[ok]      %-18s %s\n' "${command_name}" "${purpose}"
  else
    printf '[missing] %-18s %s\n' "${command_name}" "${purpose}"
    missing=1
  fi
}

echo "Maxwell Linux Lab environment check"
echo

check python3 "lab CLI"
check lspci "PCI GPU identity and bound drivers"
check vulkaninfo "Vulkan/NVK renderer inspection"
check glxinfo "OpenGL renderer inspection"
check mangohud "game frame-time logging"
check modinfo "kernel module inspection"
check lsmod "loaded module inspection"

echo
if [[ -r /sys/kernel/debug/dri/0/pstate ]] || compgen -G '/sys/kernel/debug/dri/*/pstate' >/dev/null; then
  echo "[ok]      Nouveau pstate debugfs entry is readable"
else
  echo "[info]    No readable /sys/kernel/debug/dri/*/pstate entry detected"
  echo "          This can be normal when Nouveau is not bound, debugfs is unavailable,"
  echo "          the path uses another DRI index, or permissions do not allow access."
fi

echo
if command -v nvidia-smi >/dev/null 2>&1; then
  echo "[info]    nvidia-smi is available; proprietary-driver telemetry can be captured."
else
  echo "[info]    nvidia-smi is not available; this is expected on a pure Nouveau/NVK setup."
fi

echo
if [[ "${missing}" -ne 0 ]]; then
  echo "Suggested Fedora observation tools:"
  echo "  sudo dnf install -y python3 python3-pip pciutils vulkan-tools mesa-demos mangohud"
  exit 1
fi

echo "Environment has the core observation tools."
