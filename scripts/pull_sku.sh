#!/bin/bash -p
{ builtin set +x; } 2>/dev/null
# Launch-safe SKU router. Only the exact official Q4_K_M has a compiled
# filename, byte count, and SHA-256 authority in this deployment pack.
if [[ "$-" != *p* || "${BASH_SOURCE[0]}" != "$0" ]]; then
  /usr/bin/printf '%s\n' 'FAIL-CLOSED: execute this file directly; sourcing/plain bash is unsupported' >&2
  exit 126
fi
builtin unset POSIXLY_CORRECT POSIX_PEDANTIC BASH_COMPAT GLOBIGNORE
builtin set +o posix
builtin set -euo pipefail
IFS=$' \t\n'
builtin umask 077
if (( EUID == 0 || EUID != UID )); then
  /usr/bin/printf '%s\n' 'FAIL-CLOSED: pull as one unprivileged user with matching real/effective IDs' >&2
  exit 126
fi
readonly CLEAN_PATH="/usr/local/cuda/bin:/usr/bin:/bin"
builtin export PATH="${CLEAN_PATH}"
builtin unset LD_PRELOAD LD_AUDIT LD_LIBRARY_PATH CDPATH ENV BASH_ENV TMPDIR TMP TEMP

ROOT="$(builtin cd "$(/usr/bin/dirname "${BASH_SOURCE[0]}")/.." && builtin pwd -P)"
SKU="${1:-}"

usage() {
  cat <<'EOF'
Usage: scripts/pull_sku.sh official-q4km

The public launch path downloads only poolside/Laguna-S-2.1-GGUF's exact
Q4_K_M artifact through scripts/pull_official_gguf.sh.

Historical third-party SKU names are research references, not executable
download lanes in the launch pack. They require a separate manifest with
immutable revision, filename, byte count, and SHA-256 plus an independently
audited destination/publish flow before they may be re-enabled.
EOF
  exit 2
}

[[ -n "${SKU}" ]] || usage
case "${SKU}" in
  official-q4km)
    exec "${ROOT}/scripts/pull_official_gguf.sh"
    ;;
  unsloth-ud-q4k-xl|unsloth-ud-iq4-xs|unsloth-ud-iq3-s|unsloth-ud-q2k-xl|bartowski-iq4-xs)
    echo "FAIL-CLOSED: experimental SKU ${SKU} has no audited exact-byte manifest in this launch pack" >&2
    echo "Use a separate research workspace; it cannot produce Laguna launch authority." >&2
    exit 2
    ;;
  *)
    echo "unknown SKU: ${SKU}" >&2
    usage
    ;;
esac
